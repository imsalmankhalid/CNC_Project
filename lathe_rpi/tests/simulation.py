"""
Simulation helpers for desktop testing without hardware.

These classes allow the test suite (and manual desktop runs) to inject
realistic encoder and spindle inputs to exercise the full motion pipeline.

Usage example
-------------
    from tests.simulation.encoder_sim import EncoderSimulator
    sim = EncoderSimulator(mock_hw)
    sim.simulate_handwheel_z(revolutions=2.0, rpm=60)
"""

from __future__ import annotations

import time
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hal.mock_interface import MockInterface


class EncoderSimulator:
    """Generates continuous encoder counts into a MockInterface."""

    def __init__(self, hw: "MockInterface") -> None:
        self._hw = hw

    def simulate_handwheel_z(
        self, revolutions: float, rpm: float = 60.0
    ) -> None:
        """
        Inject *revolutions* of Z handwheel rotation at *rpm*.
        Blocks until complete.
        """
        from config import Z_ENC_CNT_PER_REV
        total_counts = int(revolutions * Z_ENC_CNT_PER_REV)
        interval_s = (60.0 / rpm) / Z_ENC_CNT_PER_REV
        for _ in range(total_counts):
            self._hw.simulate_z_encoder(1)
            time.sleep(interval_s)

    def simulate_handwheel_x(
        self, revolutions: float, rpm: float = 60.0
    ) -> None:
        from config import X_ENC_CNT_PER_REV
        total_counts = int(revolutions * X_ENC_CNT_PER_REV)
        interval_s = (60.0 / rpm) / X_ENC_CNT_PER_REV
        for _ in range(total_counts):
            self._hw.simulate_x_encoder(1)
            time.sleep(interval_s)

    def simulate_handwheel_z_async(
        self, revolutions: float, rpm: float = 60.0
    ) -> threading.Thread:
        """Non-blocking version – returns a thread handle."""
        t = threading.Thread(
            target=self.simulate_handwheel_z,
            args=(revolutions, rpm),
            daemon=True,
        )
        t.start()
        return t


class SpindleSimulator:
    """Continuously fires spindle index pulses into a MockInterface."""

    def __init__(self, hw: "MockInterface") -> None:
        self._hw = hw
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self, rpm: float = 1200.0) -> None:
        """Start firing index pulses at *rpm*."""
        self._running = True
        interval_s = 60.0 / rpm
        self._thread = threading.Thread(
            target=self._loop,
            args=(interval_s,),
            daemon=True,
            name="SpindleSim",
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self, interval_s: float) -> None:
        while self._running:
            self._hw.fire_spindle_pulse()
            time.sleep(interval_s)
