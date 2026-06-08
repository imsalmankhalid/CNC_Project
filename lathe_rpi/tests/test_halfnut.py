"""
Tests for HalfNutController – electronic feed logic.
"""

import time
import pytest
from core.halfnut import HalfNutController
from core.state_manager import get_state
import config as cfg


class TestHalfNutFeed:
    """Verify that the half-nut feed thread issues the correct steps."""

    def test_no_feed_when_lever_released(self, hw_state):
        hw, state = hw_state
        hw.set_halfnut(False)
        hn = HalfNutController(hw)
        hn.poll()
        time.sleep(0.05)
        assert hw.z_steps_issued == 0, "No Z steps when lever not engaged"

    def test_feed_starts_on_lever_engage(self, hw_state):
        hw, state = hw_state
        state.feed_rate_mm = 254.0   # 10 IPM – reasonable test speed
        hw.set_halfnut(True)
        hn = HalfNutController(hw)
        hn.poll()
        # Allow feed thread to run briefly
        time.sleep(0.15)
        hn.stop_feed()
        time.sleep(0.05)
        assert hw.z_steps_issued > 0, "Z steps should be issued after lever engage"

    def test_feed_stops_when_lever_released(self, hw_state):
        hw, state = hw_state
        state.feed_rate_mm = 254.0
        hw.set_halfnut(True)
        hn = HalfNutController(hw)
        hn.poll()
        time.sleep(0.1)
        hw.set_halfnut(False)
        time.sleep(0.1)
        steps_at_stop = hw.z_steps_issued
        time.sleep(0.15)
        assert hw.z_steps_issued == steps_at_stop, \
            "No additional steps after lever release"

    def test_feed_stops_at_zstop_position(self, hw_state):
        hw, state = hw_state
        state.feed_rate_mm = 1270.0   # 50 IPM – fast so test completes quickly
        # Set Z stop at 50 motor counts ahead
        state.mtr_pos_z = 0
        state.mem_stop_z[0] = 50
        hw.set_halfnut(True)
        hn = HalfNutController(hw)
        hn.poll()
        time.sleep(0.3)
        hn.stop_feed()
        assert state.mtr_pos_z <= 50 + 5, \
            f"Feed should stop near Z-stop=50; got {state.mtr_pos_z}"

    def test_feed_does_not_move_beyond_limit_z_plus(self, hw_state):
        hw, state = hw_state
        state.feed_rate_mm = 1270.0
        state.limit_z_plus = True   # limit pre-triggered
        hw.set_halfnut(True)
        hn = HalfNutController(hw)
        hn.poll()
        time.sleep(0.15)
        hn.stop_feed()
        assert hw.z_steps_issued == 0, \
            "Feed must not move when Z+ limit is active"

    def test_encoder_reset_after_feed(self, hw_state):
        hw, state = hw_state
        state.feed_rate_mm = 1270.0
        # Set a short stop distance
        state.mtr_pos_z = 0
        state.mem_stop_z[0] = 20
        hw.set_halfnut(True)
        hn = HalfNutController(hw)
        hn.poll()
        time.sleep(0.3)
        hn.stop_feed()
        # After feed, encoder should be at its pre-feed value
        assert hw.get_z_encoder() == 0, \
            "Z encoder should be reset to pre-feed value after completion"
