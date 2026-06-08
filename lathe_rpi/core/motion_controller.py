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
  3. Only one axis moves at a time – the axis not moving has its encoder
     "frozen" to prevent phantom movement.

On the RPi this runs inside a high-priority daemon thread; the HAL issues
actual STEP pulses via pigpio waveforms (hardware-timed).
"""

from __future__ import annotations

import os
import threading
import time
from typing import TYPE_CHECKING

import config as cfg
from .state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


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

        # Freeze X encoder to prevent phantom X motion while Z moves
        x_frozen = self._hw.get_x_encoder()

        self._z_enc_buf += float(enc_new) - float(self._z_enc_old)

        while abs(self._z_enc_buf) >= cfg.Z_COUNT_ADJ_INV:
            # Clamp buffer to max (protects against spinning past max velocity)
            if abs(self._z_enc_buf) > cfg.Z_MAX_ENC_BUF:
                self._z_enc_buf = (
                    cfg.Z_MAX_ENC_BUF if self._z_enc_buf > 0 else -cfg.Z_MAX_ENC_BUF
                )

            calc_vel = (abs(self._z_enc_buf) * cfg.Z_MAX_VEL) / cfg.Z_MAX_ENC_BUF
            delay_1stp = (
                (cfg.Z_PITCH / (calc_vel * cfg.Z_MTR_CNT_PER_REV)) * 60.0 * 1_000_000.0
            )
            delay_1stp = min(delay_1stp, 24000)

            # Choose step batch size based on velocity band (matching Arduino)
            if calc_vel <= cfg.Z_VEL_LIMIT_A:
                step_size = max(1, round(8750 / delay_1stp + 0.5))
            elif calc_vel <= cfg.Z_VEL_LIMIT_B:
                step_size = max(1, round(4800 / delay_1stp + 0.5))
            elif calc_vel <= cfg.Z_VEL_LIMIT_C:
                step_size = max(1, round(4800 / delay_1stp + 0.5))
            elif calc_vel <= cfg.Z_VEL_LIMIT_D:
                step_size = max(1, round(3900 / delay_1stp + 0.5))
            else:
                step_size = max(1, round(700 / delay_1stp + 0.5))

            if self._z_enc_buf < 0:
                step_size = -step_size

            # Check limit switches before moving
            if step_size > 0 and self._state.limit_z_plus:
                break
            if step_size < 0 and self._state.limit_z_minus:
                break

            # Clamp step size so we don't overshoot the Z auto-stop
            mem_stop = self._state.mem_stop_z[self._state.active_mem_z]
            if mem_stop < 999_999:
                if step_size > 0:
                    remaining = mem_stop - self._state.mtr_pos_z
                    if remaining <= 0:
                        break
                    step_size = min(step_size, remaining)
                elif step_size < 0:
                    remaining = mem_stop - self._state.mtr_pos_z
                    if remaining >= 0:
                        break
                    step_size = max(step_size, remaining)

            # Issue motor steps
            self._hw.z_step(step_size)
            self._state.mtr_pos_z += step_size

            # Auto-stop check (catches exact landing)
            if mem_stop < 999_999:
                if self._state.mtr_pos_z == mem_stop:
                    break

            # Update buffer
            enc_new2 = self._hw.get_z_encoder()
            self._z_enc_buf = (
                self._z_enc_buf
                + float(enc_new2) - float(enc_new)
                - float(step_size) * cfg.Z_COUNT_ADJ_INV
            )
            enc_new = enc_new2

        self._z_enc_old = enc_new
        # Restore X encoder
        self._hw.set_x_encoder(x_frozen)

    # ── X-axis handwheel ─────────────────────────────────────────────────────

    def _process_x_handwheel(self) -> None:
        enc_new = self._hw.get_x_encoder()
        if enc_new == self._x_enc_old:
            return

        z_frozen = self._hw.get_z_encoder()

        self._x_enc_buf += float(enc_new) - float(self._x_enc_old)

        while abs(self._x_enc_buf) >= cfg.X_COUNT_ADJ_INV:
            if abs(self._x_enc_buf) > cfg.X_COUNT_ADJ_INV * 600:
                # Clamp X buffer (X has no explicit max buf constant in original)
                cap = cfg.X_COUNT_ADJ_INV * 600
                self._x_enc_buf = cap if self._x_enc_buf > 0 else -cap

            # Simple proportional step for X (X is accuracy-focused, not velocity)
            step_size = 1 if self._x_enc_buf > 0 else -1

            if step_size > 0 and self._state.limit_x_plus:
                break
            if step_size < 0 and self._state.limit_x_minus:
                break

            self._hw.x_step(step_size)
            self._state.mtr_pos_x += step_size

            enc_new2 = self._hw.get_x_encoder()
            self._x_enc_buf = (
                self._x_enc_buf
                + float(enc_new2) - float(enc_new)
                - float(step_size) * cfg.X_COUNT_ADJ_INV
            )
            enc_new = enc_new2

        self._x_enc_old = enc_new
        self._hw.set_z_encoder(z_frozen)

    # ── Limit switch polling ─────────────────────────────────────────────────

    def _check_limits(self) -> None:
        st = self._state
        st.limit_z_plus  = self._hw.read_limit_switch("Z", "+")
        st.limit_z_minus = self._hw.read_limit_switch("Z", "-")
        st.limit_x_plus  = self._hw.read_limit_switch("X", "+")
        st.limit_x_minus = self._hw.read_limit_switch("X", "-")

        if any([st.limit_z_plus, st.limit_z_minus, st.limit_x_plus, st.limit_x_minus]):
            # A limit is active – upper layers decide which direction to allow
            pass
