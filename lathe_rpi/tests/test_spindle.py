"""
Tests for SpindleMonitor – RPM calculation from index pulses.
"""

import time
import pytest
from core.spindle import SpindleMonitor
from core.state_manager import get_state


def _fire_pulses(hw, monitor, rpm: float, num_pulses: int) -> None:
    """Simulate spindle running at *rpm* by firing *num_pulses* index pulses."""
    interval_us = int(1_000_000 * 60.0 / rpm)
    for i in range(num_pulses):
        hw.fire_spindle_pulse()
        # Advance mock micros by manipulating start time
        hw._start_time_ns -= interval_us * 1000
        time.sleep(0.001)


class TestSpindleRpm:

    def test_rpm_zero_at_start(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        assert state.spindle_rpm == 0.0

    def test_rpm_updates_after_pulses(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        # Simulate 1200 RPM (50 000 µs interval) – fire two pulses
        interval_us = int(1_000_000 * 60.0 / 1200)
        hw._index_time_old = 0   # access internal via monitor
        sm._index_time_old = 0
        sm._index_time_new = interval_us
        sm._update_rpm()
        # RPM should now be approximately 1200
        assert 1100 < state.spindle_rpm < 1300, \
            f"Expected ~1200 RPM, got {state.spindle_rpm:.1f}"

    def test_rpm_zero_when_spindle_slow(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        # Simulate very slow spindle (1 RPM – below min)
        sm._index_time_old = 0
        sm._index_time_new = 61_000_000   # 61 s interval → > MAX_INTERVAL
        sm._update_rpm()
        assert state.spindle_rpm == 0.0

    def test_rpm_ignores_implausible_short_interval(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        initial_rpm = state.spindle_rpm
        # 1 µs interval → impossibly fast → should be ignored
        sm._index_time_old = 0
        sm._index_time_new = 1
        sm._update_rpm()
        assert state.spindle_rpm == initial_rpm, \
            "Implausible interval should not change RPM"

    def test_listener_called_on_pulse(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        called = []
        sm.add_listener(lambda: called.append(True))
        hw.fire_spindle_pulse()
        assert len(called) == 1

    def test_listener_removed_stops_callbacks(self, hw_state):
        hw, state = hw_state
        sm = SpindleMonitor(hw)
        sm.start()
        called = []
        cb = lambda: called.append(True)
        sm.add_listener(cb)
        sm.remove_listener(cb)
        hw.fire_spindle_pulse()
        assert len(called) == 0
