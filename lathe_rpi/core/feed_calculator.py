"""
Feed & Speed Calculator
=======================
Reads the potentiometer ADC value and spindle RPM from MachineState to
compute and update feed_rate_mm and feed_rate_ipm.

Ported from:  10_SpdFeed.ino  (potentiometer / calcFeed)
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

import config as cfg
from .state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


class FeedCalculator:
    """
    Polls the potentiometer at a low rate and converts the reading to a
    feed rate (mm/min and IPM).  Updates MachineState in-place.
    """

    _POLL_INTERVAL_S = 0.1  # 100 ms – no need to poll faster
    _CHANGE_THRESHOLD = 5   # raw ADC units  (= ~0.4 IPM, matching Arduino)

    def __init__(self, hw: "HardwareInterface") -> None:
        self._hw = hw
        self._state = get_state()
        self._prev_pot: int = -999
        self._anchor: int = -999
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._poll_loop, name="FeedCalc", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _poll_loop(self) -> None:
        while self._running:
            pot = self._hw.read_potentiometer()
            if abs(pot - self._anchor) > self._CHANGE_THRESHOLD:
                self._anchor = pot
                self._prev_pot = pot
                self._calc(pot)
            elif (
                abs(pot - self._prev_pot) > 1
            ):
                self._prev_pot = pot
                self._calc(pot)
            time.sleep(self._POLL_INTERVAL_S)

    def _calc(self, pot: int) -> None:
        """Map 0–1023 ADC reading to feedRateMin..feedRateMax mm/min."""
        if pot < 18:
            feed_mm = cfg.FEED_RATE_MIN_MM
        elif pot > 1007:
            feed_mm = cfg.FEED_RATE_MAX_MM
        else:
            span_adc  = 1007 - 18
            span_feed = cfg.FEED_RATE_MAX_MM - cfg.FEED_RATE_MIN_MM
            feed_mm = cfg.FEED_RATE_MIN_MM + (pot - 18) / span_adc * span_feed

        with self._state.atomic():
            self._state.feed_rate_mm = feed_mm
            self._state.feed_rate_ipm = feed_mm / 25.4
