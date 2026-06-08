"""
Profile (Taper) Mode
====================
Automated multi-point profile turning.  Operator defines up to 10 X/Z
co-ordinates; the mode interpolates linear segments between them with
automatic rough + finish passes.

Ported from:  50_Profile.ino  (taperSetup / tprMove / zTprProfile …)
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from .base_mode import BaseMode
import config as cfg

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface

MAX_PROFILE_POINTS = 10


@dataclass
class ProfileSetup:
    stock_od_mm:   float = 12.7
    stock_rad_cnt: int   = 0          # X motor counts at stock surface
    x_retract_cnt: int   = 0          # X motor counts for retract
    num_points:    int   = 3
    z_pos:  List[int] = field(default_factory=lambda: [0]*MAX_PROFILE_POINTS)
    x_rad:  List[int] = field(default_factory=lambda: [0]*MAX_PROFILE_POINTS)
    # Offsets applied after zeroing
    z_pos_offset: List[int] = field(default_factory=lambda: [0]*MAX_PROFILE_POINTS)
    x_rad_offset: List[int] = field(default_factory=lambda: [0]*MAX_PROFILE_POINTS)

    cut_depth_cnt:  int = 0    # rough pass DOC in X motor counts
    fin_depth_cnt:  int = 0    # finish pass DOC

    cut_direction:  int = 0    # 0=left(-Z), 1=right(+Z)
    pass_current:   int = 0
    pass_total:     int = 0


class ProfileMode(BaseMode):
    """Multi-point profile/taper turning mode."""

    def __init__(self, hw: "HardwareInterface") -> None:
        super().__init__(hw)
        self.step:  int = 0
        self.setup = ProfileSetup()
        self._current_point: int = 0
        self._motion_thread: Optional[threading.Thread] = None
        self._abort = False
        self._step_changed_cb = None

    def register_step_changed(self, cb) -> None:
        self._step_changed_cb = cb

    def _notify(self) -> None:
        if self._step_changed_cb:
            self._step_changed_cb(self.step)

    # ── Life-cycle ────────────────────────────────────────────────────────────

    def enter(self) -> None:
        self._active = True
        self._state.mode = 3
        self.step = 0
        self.setup = ProfileSetup()
        self._current_point = 0
        self._abort = False
        # Default DOC: 0.5 mm rough, 0.07 mm finish
        self.setup.cut_depth_cnt = int(0.5 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH)
        self.setup.fin_depth_cnt = int(0.07 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH)
        self._notify()

    def exit(self) -> None:
        self._abort = True
        self._active = False

    def tick(self) -> None:
        pass

    # ── Wizard navigation ─────────────────────────────────────────────────────

    def confirm(self) -> None:
        s = self.setup
        st = self._state
        hw = self._hw

        if self.step == 0:    # Stock OD set → record X position
            s.stock_rad_cnt = st.mtr_pos_x
            self.step = 4
        elif self.step == 4:  # X retract position confirmed
            if st.mtr_pos_x < s.stock_rad_cnt + int(
                1.0 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH
            ):
                pass  # NOK – stay on step 4
            else:
                s.x_retract_cnt = st.mtr_pos_x
                self.step = 7
        elif self.step == 7:  # Number of points selected
            self.step = 10
            self._current_point = 0
        elif self.step == 10:  # Profile point recorded
            s.z_pos[self._current_point] = st.mtr_pos_z
            s.x_rad[self._current_point] = st.mtr_pos_x
            self._current_point += 1
            if self._current_point >= s.num_points:
                self._calc_offsets()
                self.step = 20
            # else stay on 10 for next point
        elif self.step == 20:  # DOC confirmed → ready to run
            self.step = 30
            self._launch_profile()
        self._notify()

    def select_next(self) -> None:
        s = self.setup
        if self.step == 7 and s.num_points < MAX_PROFILE_POINTS:
            s.num_points += 1
        elif self.step == 20:
            s.cut_depth_cnt = max(1, s.cut_depth_cnt + int(0.05 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH))
        self._notify()

    def select_prev(self) -> None:
        s = self.setup
        if self.step == 7 and s.num_points > 2:
            s.num_points -= 1
        elif self.step == 20:
            s.cut_depth_cnt = max(1, s.cut_depth_cnt - int(0.05 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH))
        self._notify()

    # ── Geometry calculation ──────────────────────────────────────────────────

    def _calc_offsets(self) -> None:
        """Record current motor positions as zero-reference for the profile."""
        s = self.setup
        for i in range(s.num_points):
            s.z_pos_offset[i] = s.z_pos[i]
            s.x_rad_offset[i] = s.x_rad[i]

        # Estimate pass count
        x_range = max(s.x_rad[:s.num_points]) - min(s.x_rad[:s.num_points])
        rough = max(0, int(x_range / s.cut_depth_cnt))
        s.pass_total = rough + 1  # +1 finish pass

    # ── Profile execution ─────────────────────────────────────────────────────

    def _launch_profile(self) -> None:
        if self._motion_thread and self._motion_thread.is_alive():
            return
        self._abort = False
        self._motion_thread = threading.Thread(
            target=self._run_profile, daemon=True, name="ProfilePass"
        )
        self._motion_thread.start()

    def _run_profile(self) -> None:
        """
        Iterates rough passes then finish pass.
        Each pass traverses the multi-point profile using linear interpolation.
        """
        s = self.setup
        st = self._state
        hw = self._hw

        feed_mm = st.feed_rate_mm
        z_pitch = cfg.Z_PITCH
        x_pitch = cfg.X_PITCH
        z_mtr   = cfg.Z_MTR_CNT_PER_REV
        x_mtr   = cfg.X_MTR_CNT_PER_REV

        total_passes = s.pass_total

        for pass_idx in range(total_passes):
            if self._abort:
                break

            s.pass_current = pass_idx + 1
            is_finish = (pass_idx == total_passes - 1)
            doc = s.fin_depth_cnt if is_finish else s.cut_depth_cnt

            # Retract X
            hw.x_step(s.x_retract_cnt - st.mtr_pos_x)
            with st.atomic():
                st.mtr_pos_x = s.x_retract_cnt

            # Return to Z start
            hw.z_step(s.z_pos_offset[0] - st.mtr_pos_z)
            with st.atomic():
                st.mtr_pos_z = s.z_pos_offset[0]

            # Advance X to this pass depth (from stock surface)
            pass_x_target = s.stock_rad_cnt - doc * (pass_idx + 1)
            hw.x_step(pass_x_target - st.mtr_pos_x)
            with st.atomic():
                st.mtr_pos_x = pass_x_target

            # Traverse profile segments
            for seg in range(1, s.num_points):
                if self._abort:
                    break

                z_start = s.z_pos_offset[seg - 1]
                z_end   = s.z_pos_offset[seg]
                x_start = min(pass_x_target, s.x_rad_offset[seg - 1])
                x_end   = min(pass_x_target, s.x_rad_offset[seg])

                dz = z_end - z_start
                dx = x_end - x_start

                # Compute segment length and feed timing
                seg_len_mm = math.sqrt(
                    (dz * z_pitch / z_mtr) ** 2 +
                    (dx * x_pitch / x_mtr) ** 2
                )
                if seg_len_mm < 0.001:
                    continue

                # Number of interpolation steps (1-count resolution)
                steps = max(abs(dz), abs(dx), 1)
                for i in range(steps):
                    if self._abort:
                        break
                    frac = (i + 1) / steps
                    z_target = z_start + int(dz * frac)
                    x_target = x_start + int(dx * frac)
                    hz = z_target - st.mtr_pos_z
                    hx = x_target - st.mtr_pos_x
                    if hz:
                        hw.z_step(hz)
                        with st.atomic():
                            st.mtr_pos_z += hz
                    if hx:
                        hw.x_step(hx)
                        with st.atomic():
                            st.mtr_pos_x += hx

                    # Per-step delay for feed rate
                    step_mm = seg_len_mm / steps
                    step_delay = step_mm / feed_mm * 60.0
                    time.sleep(max(0.0, step_delay))

        # Final retract
        hw.x_step(s.x_retract_cnt - st.mtr_pos_x)
        with st.atomic():
            st.mtr_pos_x = s.x_retract_cnt

        self.step = 40  # "Profile Complete"
        self._notify()

    # ── UI properties ─────────────────────────────────────────────────────────

    @property
    def point_label(self) -> str:
        return f"Point {self._current_point + 1} of {self.setup.num_points}"

    @property
    def doc_mm(self) -> float:
        return self.setup.cut_depth_cnt * cfg.X_PITCH / cfg.X_MTR_CNT_PER_REV
