"""
Radius / Sphere Mode
====================
Automated internal and external arc turning (radius and full-sphere).
The cutting path traces a circular arc in the X-Z plane.

Ported from:  60_Radius.ino  (arcSetup / arcMove / …)
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .base_mode import BaseMode
import config as cfg

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


@dataclass
class RadiusSetup:
    arc_type:       int   = 0    # 0=internal, 1=external
    insert_type:    int   = 0    # 0=round, 1=diamond
    insert_rad_mm:  float = 5.0  # insert radius (mm)
    stock_od_mm:    float = 25.4
    stock_rad_cnt:  int   = 0
    x_retract_cnt:  int   = 0
    arc_radius_mm:  float = 12.7
    arc_centre_z:   int   = 0    # Z motor counts at arc centre
    arc_centre_x:   int   = 0    # X motor counts at arc centre
    cut_depth_cnt:  int   = 0
    pass_current:   int   = 0
    pass_total:     int   = 0


class RadiusMode(BaseMode):
    """Internal / external arc turning mode."""

    # Angular interpolation resolution (degrees)
    _ARC_STEP_DEG = 0.5

    def __init__(self, hw: "HardwareInterface") -> None:
        super().__init__(hw)
        self.step  = 0
        self.setup = RadiusSetup()
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
        self._state.mode = 4
        self.step = 0
        self.setup = RadiusSetup()
        self._abort = False
        self.setup.cut_depth_cnt = int(0.5 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH)
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

        if self.step == 0:    # Arc type chosen
            self.step = 2
        elif self.step == 2:  # Insert type chosen
            if s.insert_type == 0:
                s.insert_rad_mm = 5.0
            else:
                s.insert_rad_mm = 0.79375
            self.step = 4
        elif self.step == 4:  # Insert size confirmed
            self.step = 7
        elif self.step == 7:  # Touch known OD → record X
            s.stock_rad_cnt = st.mtr_pos_x
            self.step = 10
        elif self.step == 10: # Set X retract
            s.x_retract_cnt = st.mtr_pos_x
            self.step = 13
        elif self.step == 13: # Arc radius entered
            self.step = 16
        elif self.step == 16: # Touch arc centre on Z axis
            s.arc_centre_z = st.mtr_pos_z
            s.arc_centre_x = st.mtr_pos_x
            self._calc_arc_passes()
            self.step = 20
        elif self.step == 20: # DOC confirmed → launch
            self.step = 30
            self._launch_arc()
        self._notify()

    def select_next(self) -> None:
        s = self.setup
        if self.step == 0:
            s.arc_type = min(s.arc_type + 1, 1)
        elif self.step == 2:
            s.insert_type = min(s.insert_type + 1, 1)
        elif self.step == 13:
            s.arc_radius_mm = round(s.arc_radius_mm + 0.5, 1)
        elif self.step == 20:
            s.cut_depth_cnt += int(0.05 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH)
        self._notify()

    def select_prev(self) -> None:
        s = self.setup
        if self.step == 0:
            s.arc_type = max(s.arc_type - 1, 0)
        elif self.step == 2:
            s.insert_type = max(s.insert_type - 1, 0)
        elif self.step == 13:
            s.arc_radius_mm = max(1.0, round(s.arc_radius_mm - 0.5, 1))
        elif self.step == 20:
            s.cut_depth_cnt = max(1, s.cut_depth_cnt - int(0.05 * cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH))
        self._notify()

    # ── Geometry calculation ──────────────────────────────────────────────────

    def _calc_arc_passes(self) -> None:
        s = self.setup
        r_mm   = s.arc_radius_mm
        doc_mm = s.cut_depth_cnt * cfg.X_PITCH / cfg.X_MTR_CNT_PER_REV
        s.pass_total = max(1, math.ceil(r_mm / doc_mm))

    # ── Arc execution ─────────────────────────────────────────────────────────

    def _launch_arc(self) -> None:
        if self._motion_thread and self._motion_thread.is_alive():
            return
        self._abort = False
        self._motion_thread = threading.Thread(
            target=self._run_arc, daemon=True, name="ArcPass"
        )
        self._motion_thread.start()

    def _run_arc(self) -> None:
        """
        Traces a circular arc in the X-Z plane using angular interpolation.
        For each rough pass, the effective radius is reduced by DOC until
        the final finish pass cuts at the programmed radius.
        """
        s = self.setup
        st = self._state
        hw = self._hw

        r_mm        = s.arc_radius_mm
        ins_r       = s.insert_rad_mm   # tool nose radius compensation
        z_pitch     = cfg.Z_PITCH
        x_pitch     = cfg.X_PITCH
        z_mtr       = cfg.Z_MTR_CNT_PER_REV
        x_mtr       = cfg.X_MTR_CNT_PER_REV
        feed_mm     = st.feed_rate_mm

        angle_step  = math.radians(self._ARC_STEP_DEG)
        # Arc spans 90° for external (0→90°) or 180° for internal sphere
        start_ang   = 0.0
        end_ang     = math.pi / 2 if s.arc_type == 1 else math.pi

        for pass_idx in range(s.pass_total):
            if self._abort:
                break

            s.pass_current = pass_idx + 1
            is_finish = (pass_idx == s.pass_total - 1)
            pass_r_mm = r_mm if is_finish else r_mm - (s.pass_total - 1 - pass_idx) * (
                s.cut_depth_cnt * x_pitch / x_mtr
            )

            # Retract X
            hw.x_step(s.x_retract_cnt - st.mtr_pos_x)
            with st.atomic():
                st.mtr_pos_x = s.x_retract_cnt

            # Move to arc start position (Z)
            arc_start_z = s.arc_centre_z + int((pass_r_mm - ins_r) * z_mtr / z_pitch)
            hz = arc_start_z - st.mtr_pos_z
            hw.z_step(hz)
            with st.atomic():
                st.mtr_pos_z += hz

            # Plunge X to arc surface
            arc_start_x = s.arc_centre_x
            hx = arc_start_x - st.mtr_pos_x
            hw.x_step(hx)
            with st.atomic():
                st.mtr_pos_x += hx

            # Trace arc
            theta = start_ang
            while theta <= end_ang and not self._abort:
                z_off_mm = (pass_r_mm - ins_r) * math.cos(theta)
                x_off_mm = (pass_r_mm - ins_r) * math.sin(theta)

                z_target = s.arc_centre_z + int(z_off_mm * z_mtr / z_pitch)
                x_target = s.arc_centre_x + int(x_off_mm * x_mtr / x_pitch)

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

                # Feed delay based on arc step size
                arc_step_mm = abs(pass_r_mm) * angle_step
                step_delay  = arc_step_mm / feed_mm * 60.0
                time.sleep(max(0.0, step_delay))

                theta += angle_step

        # Final retract
        hw.x_step(s.x_retract_cnt - st.mtr_pos_x)
        with st.atomic():
            st.mtr_pos_x = s.x_retract_cnt

        self.step = 40  # "Arc Complete"
        self._notify()

    # ── UI properties ─────────────────────────────────────────────────────────

    @property
    def arc_type_label(self) -> str:
        return "Internal Radius" if self.setup.arc_type == 0 else "External Radius"

    @property
    def insert_type_label(self) -> str:
        return "Round" if self.setup.insert_type == 0 else "Diamond"
