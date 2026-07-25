"""
Motion Controller
=================
Real-time Z and X axis handwheel → servo motion.

Ported from:  20_HandWh_Z.ino  and  21_HandWh_X.ino

The key algorithm (unchanged from Arduino version):
  1. Read encoder, compute delta vs previous read → accumulate into buffer.
  2. While |buffer| >= Z_COUNT_ADJ_INV (i.e. ≥ 1 motor count needed),
     compute velocity from buffer size, select step-batch size to fit
     within the available LCD-update window, issue motor steps, and subtract
     from buffer.
  3. Each axis tracks its own encoder independently via a stored "old" count,
     so Z and X can be jogged at the same time.

NOTE (bench testing): Z is temporarily simplified to the same plain
±1-per-count stepping as X, with limit switches omitted, so both axes jog
smoothly together.  The original Z velocity-banding / limit / auto-stop logic
is preserved in a comment block inside _process_z_handwheel() and should be
restored for production.

On the RPi this runs inside a high-priority daemon thread; the HAL issues
actual STEP pulses via pigpio waveforms (hardware-timed).
"""

from __future__ import annotations

import os
import threading
import time
import logging
from typing import TYPE_CHECKING

import config as cfg
from .state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


log = logging.getLogger("core.motion")


def _debug_enabled() -> bool:
    if os.environ.get("LATHE_DEBUG_HAL", "").strip() in ("1", "true", "True"):
        return True
    return bool(getattr(cfg, "DEBUG_HAL", False))


class MotionController:
    """
    Drives Z and X servos from handwheel encoder inputs.

    Parameters
    ----------
    hw : HardwareInterface
        Hardware back-end (real or mock).
    poll_interval_us : int
        How often the motion loop wakes up (µs).  Default 500µs gives
        ample headroom for the pigpio wave generation overhead.
    """

    POLL_US = 500  # motion loop wake interval (µs)

    def __init__(self, hw: "HardwareInterface") -> None:
        self._hw = hw
        self._state = get_state()
        self._running = False
        self._thread: threading.Thread | None = None

        # Z encoder buffer state
        self._z_enc_old: int = 0
        self._z_enc_buf: float = 0.0

        # X encoder buffer state
        self._x_enc_old: int = 0
        self._x_enc_buf: float = 0.0

        # Last logged limit-switch snapshot (for change-only debug logging)
        self._limits_log: tuple | None = None

        self._debug = _debug_enabled()
        if self._debug:
            try:
                from log_setup import setup_logging
                setup_logging()
            except Exception:
                if not logging.getLogger().handlers:
                    logging.basicConfig(level=logging.DEBUG)
            log.setLevel(logging.DEBUG)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the background motion control thread."""
        self._z_enc_old = self._hw.get_z_encoder()
        self._x_enc_old = self._hw.get_x_encoder()
        self._running = True
        self._thread = threading.Thread(
            target=self._motion_loop, name="MotionControl", daemon=True
        )
        self._thread.start()
        # Try to elevate thread priority (requires root on Linux)
        try:
            os.sched_setscheduler(
                0,
                os.SCHED_FIFO,
                os.sched_param(os.sched_get_priority_max(os.SCHED_FIFO)),
            )
        except (AttributeError, PermissionError):
            pass  # Not on Linux or insufficient privileges – acceptable in testing

    def stop(self) -> None:
        """Stop the motion control thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    # ── Motion loop ───────────────────────────────────────────────────────────

    def _motion_loop(self) -> None:
        while self._running:
            t_start = self._hw.micros()

            if not self._state.estop and self._state.mode in (0, 3, 4):
                self._process_z_handwheel()
                self._process_x_handwheel()

            self._check_limits()

            elapsed = self._hw.micros() - t_start
            remaining = self.POLL_US - elapsed
            if remaining > 0:
                time.sleep(remaining / 1_000_000)

    # ── Z-axis handwheel ─────────────────────────────────────────────────────

    def _process_z_handwheel(self) -> None:
        enc_new = self._hw.get_z_encoder()
        if enc_new == self._z_enc_old:
            return

        # Whole-axis limit switch (GPIO 16): while hit, the Z motor must not
        # move.  Track the encoder but emit no steps and keep the buffer empty,
        # so jogging resumes cleanly once the switch releases.
        if self._state.limit_z:
            if self._debug:
                log.debug("Z motion BLOCKED – limit_z active (enc=%d)", enc_new)
            self._z_enc_old = enc_new
            self._z_enc_buf = 0.0
            return

        if self._debug:
            log.debug("Z handwheel: enc %d -> %d (delta %+d), buf %.1f",
                      self._z_enc_old, enc_new, enc_new - self._z_enc_old,
                      self._z_enc_buf)

        self._z_enc_buf += float(enc_new) - float(self._z_enc_old)

        # ------------------------------------------------------------------
        # TEMPORARY (bench testing): Z uses the SAME simple ±1-per-count
        # stepping as the X axis so both axes jog smoothly together.  A simple
        # whole-axis limit block (above) IS active, but the richer Arduino-style
        # Z behaviour is preserved below and should be restored for production:
        #
        #   1. Velocity banding — pick a step BATCH size from the handwheel
        #      speed (calc_vel) so a fast spin emits many steps per cycle
        #      (fast rapid jog), while a slow spin emits single steps:
        #
        #        calc_vel = (abs(self._z_enc_buf) * cfg.Z_MAX_VEL) / cfg.Z_MAX_ENC_BUF
        #        delay_1stp = (cfg.Z_PITCH / (calc_vel * cfg.Z_MTR_CNT_PER_REV)) \
        #                     * 60.0 * 1_000_000.0
        #        delay_1stp = min(delay_1stp, 24000)
        #        if   calc_vel <= cfg.Z_VEL_LIMIT_A: step_size = max(1, round(8750 / delay_1stp + 0.5))
        #        elif calc_vel <= cfg.Z_VEL_LIMIT_B: step_size = max(1, round(4800 / delay_1stp + 0.5))
        #        elif calc_vel <= cfg.Z_VEL_LIMIT_C: step_size = max(1, round(4800 / delay_1stp + 0.5))
        #        elif calc_vel <= cfg.Z_VEL_LIMIT_D: step_size = max(1, round(3900 / delay_1stp + 0.5))
        #        else:                               step_size = max(1, round(700  / delay_1stp + 0.5))
        #        if self._z_enc_buf < 0: step_size = -step_size
        #
        #   2. Limit switches — stop before driving into an end stop:
        #        if step_size > 0 and self._state.limit_z_plus:  break
        #        if step_size < 0 and self._state.limit_z_minus: break
        #
        #   3. Z auto-stop (mem_stop_z) — clamp step_size so the axis lands
        #      exactly on the stored Z-stop position and does not overshoot.
        #
        # To re-enable, replace the simple loop below with the logic above
        # (also see git history for the full original implementation).
        # ------------------------------------------------------------------

        while abs(self._z_enc_buf) >= cfg.Z_COUNT_ADJ_INV:
            # Clamp buffer to protect against runaway when spun very fast
            if abs(self._z_enc_buf) > cfg.Z_MAX_ENC_BUF:
                self._z_enc_buf = (
                    cfg.Z_MAX_ENC_BUF if self._z_enc_buf > 0 else -cfg.Z_MAX_ENC_BUF
                )

            # Simple proportional step, identical to the X axis
            step_size = 1 if self._z_enc_buf > 0 else -1

            self._hw.z_step(step_size)
            self._state.mtr_pos_z += step_size

            if self._debug:
                log.debug("Z step %+d -> mtr_pos_z=%d",
                          step_size, self._state.mtr_pos_z)

            # Update buffer
            enc_new2 = self._hw.get_z_encoder()
            self._z_enc_buf = (
                self._z_enc_buf
                + float(enc_new2) - float(enc_new)
                - float(step_size) * cfg.Z_COUNT_ADJ_INV
            )
            enc_new = enc_new2

        self._z_enc_old = enc_new

    # ── X-axis handwheel ─────────────────────────────────────────────────────

    def _process_x_handwheel(self) -> None:
        enc_new = self._hw.get_x_encoder()
        if enc_new == self._x_enc_old:
            return

        # Whole-axis limit switch (GPIO 8): while hit, the X motor must not
        # move.  Track the encoder but emit no steps and keep the buffer empty.
        if self._state.limit_x:
            if self._debug:
                log.debug("X motion BLOCKED – limit_x active (enc=%d)", enc_new)
            self._x_enc_old = enc_new
            self._x_enc_buf = 0.0
            return

        if self._debug:
            log.debug("X handwheel: enc %d -> %d (delta %+d), buf %.1f",
                      self._x_enc_old, enc_new, enc_new - self._x_enc_old,
                      self._x_enc_buf)

        self._x_enc_buf += float(enc_new) - float(self._x_enc_old)

        while abs(self._x_enc_buf) >= cfg.X_COUNT_ADJ_INV:
            if abs(self._x_enc_buf) > cfg.X_COUNT_ADJ_INV * 600:
                # Clamp X buffer (X has no explicit max buf constant in original)
                cap = cfg.X_COUNT_ADJ_INV * 600
                self._x_enc_buf = cap if self._x_enc_buf > 0 else -cap

            # Simple proportional step for X (X is accuracy-focused, not velocity)
            step_size = 1 if self._x_enc_buf > 0 else -1

            if step_size > 0 and self._state.limit_x_plus:
                if self._debug:
                    log.debug("X+ step BLOCKED by limit_x_plus (buf %.1f)",
                              self._x_enc_buf)
                break
            if step_size < 0 and self._state.limit_x_minus:
                if self._debug:
                    log.debug("X- step BLOCKED by limit_x_minus (buf %.1f)",
                              self._x_enc_buf)
                break

            self._hw.x_step(step_size)
            self._state.mtr_pos_x += step_size

            if self._debug:
                log.debug("X step %+d -> mtr_pos_x=%d",
                          step_size, self._state.mtr_pos_x)

            enc_new2 = self._hw.get_x_encoder()
            self._x_enc_buf = (
                self._x_enc_buf
                + float(enc_new2) - float(enc_new)
                - float(step_size) * cfg.X_COUNT_ADJ_INV
            )
            enc_new = enc_new2

        self._x_enc_old = enc_new

    # ── Limit switch polling ─────────────────────────────────────────────────

    def _check_limits(self) -> None:
        st = self._state
        # Bench-test escape hatch: with no limit switches wired, a floating / NC
        # limit pin reads as triggered and silently blocks motion.  Disabling
        # limits forces them all inactive.
        if not getattr(cfg, "LIMITS_ENABLED", True):
            st.limit_z_plus = st.limit_z_minus = False
            st.limit_x_plus = st.limit_x_minus = False
            st.limit_z = st.limit_x = False
            return

        st.limit_z_plus  = self._hw.read_limit_switch("Z", "+")
        st.limit_z_minus = self._hw.read_limit_switch("Z", "-")
        st.limit_x_plus  = self._hw.read_limit_switch("X", "+")
        st.limit_x_minus = self._hw.read_limit_switch("X", "-")

        # Whole-axis limit: a single switch per axis (Z→GPIO16, X→GPIO8) trips
        # either direction.  Motion on that axis is blocked while True.
        st.limit_z = st.limit_z_plus or st.limit_z_minus
        st.limit_x = st.limit_x_plus or st.limit_x_minus

        if self._debug:
            snapshot = (st.limit_z, st.limit_x)
            if snapshot != self._limits_log:
                self._limits_log = snapshot
                log.debug("limits: Z=%s X=%s", st.limit_z, st.limit_x)
