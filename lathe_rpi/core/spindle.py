"""
Spindle Monitor
===============
Reads the single-hole index pulse (AutoTech C3 sensor) and maintains
accurate RPM using the same rolling-anchor algorithm as the Arduino code.

Ported from:  10_SpdFeed.ino  (spindRevCount / spindIndex / calcSpeed)
"""

from __future__ import annotations

import threading
from typing import Callable, Optional, TYPE_CHECKING

from .state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


class SpindleMonitor:
    """
    Registers a hardware interrupt callback on the spindle index pin and
    updates MachineState.spindle_rpm on every revolution.
    """

    # Maximum inter-pulse interval to still consider spindle "running" (µs)
    # 30 000 000 µs = 2 RPM
    _MAX_INTERVAL_US = 30_000_000
    # Minimum inter-pulse interval (µs) for max RPM guard
    # derived from 2060 RPM → ~29 100 µs / rev
    _MIN_INTERVAL_US = 28_000

    # RPM change thresholds (mimics Arduino sAnchor / sRpmN logic)
    _ANCHOR_THRESHOLD = 20    # RPM delta to reset anchor
    _QUICK_THRESHOLD  = 3     # RPM delta within 2500 ms quick-update window
    _QUICK_WINDOW_MS  = 2500

    def __init__(self, hw: "HardwareInterface") -> None:
        self._hw = hw
        self._state = get_state()

        # Timing state (µs)
        self._index_time_new: int = 0
        self._index_time_old: int = 0

        # RPM tracking
        self._rpm_new: float = 0.0
        self._rpm_old: float = 0.0
        self._rpm_anchor: float = 0.0

        # Elapsed-time tracking (ms) for quick-update window
        self._elapse_new: int = 0
        self._elapse_old: int = 0

        self._lock = threading.Lock()

        # Optional external listeners (e.g. threading mode)
        self._listeners: list[Callable[[], None]] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Register hardware callback."""
        self._hw.register_spindle_callback(self._on_index_pulse)

    def add_listener(self, cb: Callable[[], None]) -> None:
        """Add a callback fired on every index pulse (used by threading mode)."""
        self._listeners.append(cb)

    def remove_listener(self, cb: Callable[[], None]) -> None:
        if cb in self._listeners:
            self._listeners.remove(cb)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _on_index_pulse(self) -> None:
        """Called from interrupt context on every spindle revolution."""
        now_us = self._hw.micros()
        with self._lock:
            self._index_time_old = self._index_time_new
            self._index_time_new = now_us
            self._update_rpm()

        # Notify threading-mode listener
        for cb in self._listeners:
            cb()

    def _update_rpm(self) -> None:
        delta = self._index_time_new - self._index_time_old
        if delta <= 0:
            return

        # Guard: ignore implausible readings
        if delta < self._MIN_INTERVAL_US or delta > self._MAX_INTERVAL_US:
            if delta >= self._MAX_INTERVAL_US:
                self._state.spindle_rpm = 0.0
            return

        new_rpm = 1_000_000.0 * 60.0 / delta
        import time as _time
        now_ms = int(_time.monotonic() * 1000)

        if abs(new_rpm - self._rpm_anchor) > self._ANCHOR_THRESHOLD:
            self._rpm_old = new_rpm
            self._rpm_anchor = new_rpm
            self._elapse_old = self._elapse_new
            self._elapse_new = now_ms
            self._state.spindle_rpm = new_rpm
        elif (
            (now_ms - self._elapse_new) <= self._QUICK_WINDOW_MS
            and abs(new_rpm - self._rpm_old) > self._QUICK_THRESHOLD
        ):
            self._rpm_old = new_rpm
            self._elapse_new = now_ms
            self._state.spindle_rpm = new_rpm

        self._rpm_new = new_rpm

    @property
    def index_time_us(self) -> int:
        """Timestamp of the most recent index pulse (µs)."""
        return self._index_time_new

    @property
    def prev_index_time_us(self) -> int:
        return self._index_time_old
