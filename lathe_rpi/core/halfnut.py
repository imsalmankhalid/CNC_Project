"""
Electronic Half-Nut Feed
========================
Drives the Z axis at a constant mm/min feed rate (set by the potentiometer)
when the half-nut lever switch is engaged, and stops automatically when the
optional Z-stop position is reached.

Ported from:  30_HalfNut.ino  (zMotorFeed)

Key differences from Arduino version
--------------------------------------
* A dedicated thread is launched instead of a blocking while-loop, so the UI
  and spindle monitoring remain responsive during a feed pass.
* The STEP delay is achieved with time.sleep (rather than delayMicroseconds)
  which is accurate enough at the feed-rate speeds involved (ms-range delays).
* After the feed, encoder write-back still resets virtual position tracking.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

import config as cfg
from .state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


class HalfNutController:
    """Manages electronic feed triggered by the half-nut lever."""

    # Estimated Python overhead per iteration (µs) – tuned empirically
    _CODE_OVERHEAD_US = 50

    def __init__(self, hw: "HardwareInterface") -> None:
        self._hw = hw
        self._state = get_state()
        self._running = False
        self._feed_thread: threading.Thread | None = None
        self._prev_lever: bool = False

    # ── Public API ────────────────────────────────────────────────────────────

    def poll(self) -> None:
        """
        Call this regularly (e.g. every 10 ms from the main loop).
        Detects lever engagement edge and starts/stops the feed thread.
        """
        current = self._hw.read_halfnut()

        if not current:
            self._prev_lever = False
            return

        # Rising edge: lever just engaged
        if current and not self._prev_lever:
            time.sleep(0.05)  # 50 ms debounce
            if self._hw.read_halfnut():  # still engaged after debounce
                self._prev_lever = True
                self._start_feed()

    def stop_feed(self) -> None:
        """Forcibly abort an in-progress feed (e.g. operator releases lever)."""
        self._running = False

    # ── Feed thread ───────────────────────────────────────────────────────────

    def _start_feed(self) -> None:
        if self._feed_thread and self._feed_thread.is_alive():
            return  # already running
        self._running = True
        self._feed_thread = threading.Thread(
            target=self._feed_loop, name="HalfNutFeed", daemon=True
        )
        self._feed_thread.start()

    def _feed_loop(self) -> None:
        """
        Mirror of Arduino zMotorFeed() while loop.
        Runs until lever released, stop position reached, or limit triggered.
        """
        state = self._state
        feed_mm = state.feed_rate_mm      # mm/min – snapshot at engage time
        z_pitch = cfg.Z_PITCH
        mtr_cnt = cfg.Z_MTR_CNT_PER_REV

        # --- Step size (same formula as Arduino) ---
        step_float = cfg.MTR_MIN_DELAY_US * feed_mm * mtr_cnt / (60.0 * 1_000_000.0 * z_pitch)
        step_size = max(1, round(step_float + 0.5))

        # --- Delay per step batch (seconds) ---
        delay_s = (
            1.0
            / ((feed_mm / z_pitch) * (mtr_cnt / step_size))
            / 60.0
            - self._CODE_OVERHEAD_US / 1_000_000.0
        )
        delay_s = max(0.0, delay_s)

        # --- Snapshot positions for encoder reset after feed ---
        temp_mtr_z = state.mtr_pos_z
        temp_enc_z = self._hw.get_z_encoder()
        temp_enc_x = self._hw.get_x_encoder()

        # --- How far to move ---
        mem_stop = state.mem_stop_z[state.active_mem_z]
        if mem_stop < 999_999 and mem_stop > temp_mtr_z:
            move_dist = abs(temp_mtr_z - mem_stop)
        else:
            move_dist = cfg.Z_MAX_MTR_CNT

        # --- Pre-step remainder (so we land exactly on stop count) ---
        pre_step = 0
        if step_size > 1 and mem_stop < 999_999 and mem_stop > temp_mtr_z:
            pre_step = round(
                ((abs(temp_mtr_z - mem_stop) / step_size)
                 - int(abs(temp_mtr_z - mem_stop) / step_size))
                * step_size
            )

        actual_moved = 0

        while self._running:
            # --- Stop if lever released ---
            if not self._hw.read_halfnut():
                break

            # --- Stop if limit triggered ---
            if state.limit_z_plus:
                break

            # Wait the calculated delay
            if delay_s > 0:
                time.sleep(delay_s)

            # Issue step(s)
            if pre_step > 0:
                self._hw.z_step(pre_step)
                actual_moved += pre_step
                pre_step = 0
            else:
                self._hw.z_step(step_size)
                actual_moved += step_size

            # Check stop condition
            if actual_moved >= move_dist:
                break

        # --- Encoder reset (same as Arduino post-feed housekeeping) ---
        self._hw.set_z_encoder(temp_enc_z)
        self._hw.set_x_encoder(temp_enc_x)
        with state.atomic():
            state.mtr_pos_z = temp_mtr_z + actual_moved

        self._running = False
