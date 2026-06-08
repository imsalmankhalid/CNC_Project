"""
Tests for FeedCalculator – potentiometer → feed rate mapping.
"""

import time
import pytest
from core.feed_calculator import FeedCalculator
import config as cfg


class TestFeedCalculator:
    """Verify ADC-to-feed-rate conversion matches Arduino calcFeed() logic."""

    def _calc_once(self, hw, state, pot_value: int) -> tuple:
        """Helper: set pot, run one calculation, return (feed_mm, feed_ipm)."""
        hw.set_pot_value(pot_value)
        fc = FeedCalculator(hw)
        fc._calc(pot_value)
        return state.feed_rate_mm, state.feed_rate_ipm

    def test_min_pot_gives_min_feed(self, hw_state):
        hw, state = hw_state
        feed_mm, feed_ipm = self._calc_once(hw, state, 0)
        assert abs(feed_mm - cfg.FEED_RATE_MIN_MM) < 0.1, \
            f"Pot=0 should give min feed {cfg.FEED_RATE_MIN_MM:.1f} mm/min, got {feed_mm:.2f}"

    def test_max_pot_gives_max_feed(self, hw_state):
        hw, state = hw_state
        feed_mm, feed_ipm = self._calc_once(hw, state, 1023)
        assert abs(feed_mm - cfg.FEED_RATE_MAX_MM) < 1.0, \
            f"Pot=1023 should give max feed {cfg.FEED_RATE_MAX_MM:.1f} mm/min, got {feed_mm:.2f}"

    def test_midpoint_pot_is_within_range(self, hw_state):
        hw, state = hw_state
        feed_mm, _ = self._calc_once(hw, state, 512)
        assert cfg.FEED_RATE_MIN_MM < feed_mm < cfg.FEED_RATE_MAX_MM, \
            f"Mid-pot feed {feed_mm:.2f} should be between min and max"

    def test_feed_ipm_is_feed_mm_over_25_4(self, hw_state):
        hw, state = hw_state
        for pot in (100, 512, 900):
            feed_mm, feed_ipm = self._calc_once(hw, state, pot)
            assert abs(feed_ipm - feed_mm / 25.4) < 0.01, \
                f"IPM mismatch at pot={pot}: {feed_ipm:.3f} vs {feed_mm/25.4:.3f}"

    def test_feed_monotonically_increasing(self, hw_state):
        hw, state = hw_state
        prev_feed = 0.0
        for pot in range(20, 1010, 50):
            feed_mm, _ = self._calc_once(hw, state, pot)
            assert feed_mm >= prev_feed, \
                f"Feed should increase monotonically; dropped at pot={pot}"
            prev_feed = feed_mm

    def test_pot_near_lower_clamp(self, hw_state):
        hw, state = hw_state
        feed_mm, _ = self._calc_once(hw, state, 10)   # < 18 clamp threshold
        assert abs(feed_mm - cfg.FEED_RATE_MIN_MM) < 0.01

    def test_pot_near_upper_clamp(self, hw_state):
        hw, state = hw_state
        feed_mm, _ = self._calc_once(hw, state, 1020)  # > 1007 clamp
        assert abs(feed_mm - cfg.FEED_RATE_MAX_MM) < 0.01
