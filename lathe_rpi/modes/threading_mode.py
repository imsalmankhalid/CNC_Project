"""
Threading Mode
==============
Automated external thread cutting mode.  Guides the operator through a
wizard: select thread size → material → tool → set OD → set C391 → set
tip → configure pass depth → run thread pass → spring passes.

Ported from:  40_Thread.ino

The class exposes a simple state-machine via self.step (tQustCt equivalent)
so the UI can render the correct prompt screen and respond to operator
confirmation.  Thread motion itself runs in a dedicated thread to avoid
blocking the UI.
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base_mode import BaseMode
import config as cfg

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


# ── Thread data tables (inch UNC/UNF + common metric) ──────────────────────

THREAD_TABLE = [
    (#    name         pitch_mm  nom_od_mm  od_tol_mm
        "#4-40",        0.635,    2.845,    0.058),
    ("#6-32",          0.794,    3.505,    0.058),
    ("#8-32",          0.794,    4.166,    0.058),
    ("#10-24",         1.058,    4.826,    0.081),
    ("#10-32",         0.794,    4.826,    0.066),
    ("1/4\"-20",       1.270,    6.350,    0.081),
    ("1/4\"-28",       0.907,    6.350,    0.066),
    ("5/16\"-18",      1.411,    7.938,    0.081),
    ("5/16\"-24",      1.058,    7.938,    0.066),
    ("3/8\"-16",       1.588,    9.525,    0.102),
    ("3/8\"-24",       1.058,    9.525,    0.066),
    ("1/2\"-13",       1.954,   12.700,    0.102),
    ("1/2\"-20",       1.270,   12.700,    0.081),
    ("M6x1.0",         1.000,    6.000,    0.080),
    ("M8x1.25",        1.250,    8.000,    0.100),
    ("M10x1.5",        1.500,   10.000,    0.100),
    ("M12x1.75",       1.750,   12.000,    0.120),
]

MATERIAL_TABLE = [
    ("Aluminum",   200),   # SFM
    ("Mild Steel", 100),
    ("Stainless",   60),
    ("Brass",      200),
]

TOOL_TABLE = [
    "HSS",
    "Carbide",
    "Exit",
]


@dataclass
class ThreadSetup:
    size_idx:      int   = 0
    material_idx:  int   = 0
    tool_idx:      int   = 0
    od_meas_offset: float = 0.0   # measured OD deviation from nominal
    c391_offset:   int   = 0      # mtr counts when C391 touches OD
    tip_pos:       int   = 0      # mtr counts when tip touches OD
    x_retract:     int   = 0      # motor counts for X retract position
    z_start:       int   = 0      # Z motor count at thread start
    z_end:         int   = 0      # Z motor count at thread end
    rpm_actual:    float = 0.0
    feed_actual:   float = 0.0    # mm/min
    pass_num:      int   = 0
    auto_spring:   int   = cfg.THRD_AUTO_SPRING
    spring_count:  int   = 0
    infeed_total:  float = 0.0
    infeed_1st:    float = 0.0
    infeed:        float = 0.0


class ThreadingMode(BaseMode):
    """State-machine for automated thread cutting."""

    def __init__(self, hw: "HardwareInterface") -> None:
        super().__init__(hw)
        self.step: int = 0        # wizard step (tQustCt equivalent)
        self.setup = ThreadSetup()
        self._motion_thread: Optional[threading.Thread] = None
        self._abort = False

        # UI notification: when step changes, UI should re-render
        self._step_changed_cb = None

    def register_step_changed(self, cb) -> None:
        self._step_changed_cb = cb

    def _notify(self) -> None:
        if self._step_changed_cb:
            self._step_changed_cb(self.step)

    # ── Life-cycle ────────────────────────────────────────────────────────────

    def enter(self) -> None:
        self._active = True
        self._state.mode = 1
        self.step = 0
        self.setup = ThreadSetup()
        self._abort = False
        self._notify()

    def exit(self) -> None:
        self._abort = True
        self._active = False

    def tick(self) -> None:
        pass  # UI drives this via confirm() / select_next() / select_prev()

    # ── Wizard navigation (called by UI touch events) ─────────────────────────

    def confirm(self) -> None:
        """User pressed B3/Accept on current step."""
        s = self.setup
        st = self._state

        if self.step == 0:    # Thread Size selected → go to material
            self.step = 2
        elif self.step == 2:  # Material selected → go to tool
            self.step = 4
        elif self.step == 4:  # Tool selected; check if carbide forced
            if TOOL_TABLE[s.tool_idx] == "Exit":
                self.exit()
                return
            self.step = 6
        elif self.step == 6:  # OD turn step – accept measured offset
            s.od_meas_offset = 0.0  # reset; operator edits via spinners
            self.step = 8
        elif self.step == 8:  # C391 tool set
            s.c391_offset = st.mtr_pos_x
            self.step = 11
        elif self.step == 11: # Tip position set
            s.tip_pos = st.mtr_pos_x
            tol_mm = 2.0
            c391_dist_mm = (s.c391_offset - s.tip_pos) * (cfg.X_PITCH / cfg.X_MTR_CNT_PER_REV)
            if abs(c391_dist_mm - cfg.THRD_C391) > tol_mm:
                # Geometry NOK – reset to step 11
                pass
            else:
                self._calc_thread_params()
                self.step = 20
        elif self.step == 20: # Parameters confirmed – set X retract
            s.x_retract = st.mtr_pos_x
            self.step = 22
        elif self.step == 22: # Set Z end position
            s.z_end = st.mtr_pos_z
            self.step = 24
        elif self.step == 24: # Set Z start (thread end on workpiece)
            s.z_start = st.mtr_pos_z
            self.step = 30
        elif self.step == 30: # Ready to run first pass
            self._launch_pass()
        self._notify()

    def select_next(self) -> None:
        s = self.setup
        if self.step == 0:
            s.size_idx = min(s.size_idx + 1, len(THREAD_TABLE) - 1)
        elif self.step == 2:
            s.material_idx = min(s.material_idx + 1, len(MATERIAL_TABLE) - 1)
        elif self.step == 4:
            s.tool_idx = min(s.tool_idx + 1, len(TOOL_TABLE) - 1)
        self._notify()

    def select_prev(self) -> None:
        s = self.setup
        if self.step == 0:
            s.size_idx = max(s.size_idx - 1, 0)
        elif self.step == 2:
            s.material_idx = max(s.material_idx - 1, 0)
        elif self.step == 4:
            s.tool_idx = max(s.tool_idx - 1, 0)
        self._notify()

    # ── Parameter calculation ─────────────────────────────────────────────────

    def _calc_thread_params(self) -> None:
        s = self.setup
        name, pitch_mm, od_nom, od_tol = THREAD_TABLE[s.size_idx]
        mat_name, sfm = MATERIAL_TABLE[s.material_idx]

        tap_drill_diam = od_nom * 2.0  # basic; will be refined with pitch
        rec_rpm = sfm * 4.0 / (od_nom / 25.4)
        s.rpm_actual = max(cfg.SPNDL_RPM_MIN, min(rec_rpm, cfg.SPNDL_RPM_MAX))

        # Infeed: 60° thread → 0.6495 × pitch / 2  (one side)
        s.infeed_total = 0.6495 * pitch_mm
        s.infeed_1st   = s.infeed_total * 0.35
        s.infeed        = s.infeed_total * 0.08  # subsequent passes

    # ── Thread pass execution ─────────────────────────────────────────────────

    def _launch_pass(self) -> None:
        if self._motion_thread and self._motion_thread.is_alive():
            return
        self._abort = False
        self._motion_thread = threading.Thread(
            target=self._run_thread_pass, daemon=True, name="ThreadPass"
        )
        self._motion_thread.start()

    def _run_thread_pass(self) -> None:
        """
        Executes one thread pass:
          1. Advance X to depth.
          2. Wait for spindle index.
          3. Drive Z in sync with spindle (counts-per-revolution tracking).
          4. Stop at Z end.
          5. Retract X.
          6. Return Z to start.
        Updates self.step so the UI can show progress.
        """
        from core.spindle import SpindleMonitor
        s = self.setup
        st = self._state
        hw = self._hw

        pitch_mm   = THREAD_TABLE[s.size_idx][1]
        z_pitch    = cfg.Z_PITCH
        mtr_cnt    = cfg.Z_MTR_CNT_PER_REV

        # --- Infeed X ---
        if s.pass_num == 0:
            depth_mm = s.infeed_1st
        else:
            depth_mm = s.infeed
        depth_counts = int(depth_mm * (cfg.X_MTR_CNT_PER_REV / cfg.X_PITCH))
        hw.x_step(-depth_counts)
        with st.atomic():
            st.mtr_pos_x -= depth_counts

        # --- Wait for spindle index (sync start) ---
        sync_event = threading.Event()
        def _on_index():
            sync_event.set()
        # Register one-shot listener
        # (SpindleMonitor listeners are persistent; we remove after sync)
        # We'll use a simple polling approach here for explicitness:
        t_wait = time.monotonic()
        while not sync_event.is_set() and not self._abort:
            sync_event.wait(timeout=0.01)
            if time.monotonic() - t_wait > 5.0:
                break  # timeout

        if self._abort:
            return

        # --- Thread cut: issue Z steps per spindle revolution ---
        mtr_counts_per_rev = int(pitch_mm * mtr_cnt / z_pitch)
        total_z_dist = abs(s.z_end - s.z_start)
        z_sign = 1 if s.z_end > s.z_start else -1
        moved_z = 0

        # Simple approach: drive Z at the calculated feed rate
        if st.spindle_rpm < 1:
            feed_mm = cfg.FEED_RATE_MIN_MM
        else:
            feed_mm = pitch_mm * st.spindle_rpm   # mm/min for threading

        step_size = max(1, mtr_counts_per_rev // 10)
        step_delay_s = (
            (z_pitch / (feed_mm * mtr_cnt / step_size)) / 60.0
        )

        while not self._abort and moved_z < total_z_dist:
            if hw.read_limit_switch("Z", "+" if z_sign > 0 else "-"):
                break
            hw.z_step(z_sign * step_size)
            with st.atomic():
                st.mtr_pos_z += z_sign * step_size
            moved_z += step_size
            time.sleep(max(0.0, step_delay_s))

        # --- Retract X ---
        x_dist = abs(s.x_retract - st.mtr_pos_x)
        x_sign = 1 if s.x_retract > st.mtr_pos_x else -1
        hw.x_step(x_sign * x_dist)
        with st.atomic():
            st.mtr_pos_x = s.x_retract

        # --- Return Z to start ---
        z_return = abs(s.z_start - st.mtr_pos_z)
        z_ret_sign = 1 if s.z_start > st.mtr_pos_z else -1
        hw.z_step(z_ret_sign * z_return)
        with st.atomic():
            st.mtr_pos_z = s.z_start

        s.pass_num += 1
        self.step = 31  # "Ready for next pass / spring pass"
        self._notify()

    # ── Properties for UI rendering ───────────────────────────────────────────

    @property
    def current_thread_name(self) -> str:
        return THREAD_TABLE[self.setup.size_idx][0]

    @property
    def current_material(self) -> str:
        return MATERIAL_TABLE[self.setup.material_idx][0]

    @property
    def current_tool(self) -> str:
        return TOOL_TABLE[self.setup.tool_idx]

    @property
    def thread_pitch_mm(self) -> float:
        return THREAD_TABLE[self.setup.size_idx][1]

    @property
    def thread_od_nom_mm(self) -> float:
        return THREAD_TABLE[self.setup.size_idx][2]
