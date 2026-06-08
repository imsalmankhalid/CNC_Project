"""
Hardware Abstraction Layer – abstract base class.

Every hardware back-end (real RPi via pigpio, or mock for testing) must
implement this interface.  The rest of the application only talks to this
interface, so the same Python code runs on a desktop (mock) and on the RPi.
"""

from __future__ import annotations
import abc
from typing import Callable


class HardwareInterface(abc.ABC):
    """Abstract description of all hardware operations required by the lathe."""

    # ── Life-cycle ──────────────────────────────────────────────────────────

    @abc.abstractmethod
    def initialise(self) -> None:
        """Set up GPIO, start background services, etc."""

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Release all GPIO, stop background services cleanly."""

    # ── Encoders ────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def get_z_encoder(self) -> int:
        """Return current Z-axis quadrature encoder count (signed integer)."""

    @abc.abstractmethod
    def set_z_encoder(self, value: int) -> None:
        """Overwrite the Z encoder accumulator (used to sync after feed)."""

    @abc.abstractmethod
    def get_x_encoder(self) -> int:
        """Return current X-axis quadrature encoder count."""

    @abc.abstractmethod
    def set_x_encoder(self, value: int) -> None:
        """Overwrite the X encoder accumulator."""

    # ── Servos ──────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def z_step(self, counts: int) -> None:
        """
        Command the Z servo to move *counts* motor steps.
        Positive = +Z direction.  The implementation handles STEP/DIR timing.
        """

    @abc.abstractmethod
    def x_step(self, counts: int) -> None:
        """Command the X servo to move *counts* motor steps."""

    @abc.abstractmethod
    def enable_z_motor(self, enabled: bool) -> None:
        """Assert / de-assert the Z servo ENABLE line."""

    @abc.abstractmethod
    def enable_x_motor(self, enabled: bool) -> None:
        """Assert / de-assert the X servo ENABLE line."""

    # ── Spindle ─────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def register_spindle_callback(self, cb: Callable[[], None]) -> None:
        """
        Register a zero-argument callback that fires on every spindle index
        pulse (once per revolution).
        """

    # ── Potentiometer (via ADC) ─────────────────────────────────────────────

    @abc.abstractmethod
    def read_potentiometer(self) -> int:
        """
        Return raw ADC reading in the range 0–1023 (10-bit equivalent),
        matching the Arduino analogRead() range used in calcFeed().
        """

    # ── Digital inputs ──────────────────────────────────────────────────────

    @abc.abstractmethod
    def read_button(self, btn_id: int) -> bool:
        """
        Return True when button *btn_id* (1, 2, 3) is currently pressed.
        Debounce is handled inside HardwareInterface implementations; callers
        see clean logical state.
        """

    @abc.abstractmethod
    def read_halfnut(self) -> bool:
        """Return True when the half-nut lever switch is engaged (HIGH)."""

    @abc.abstractmethod
    def read_limit_switch(self, axis: str, direction: str) -> bool:
        """
        Return True when the specified limit switch is triggered.

        Parameters
        ----------
        axis      : "X" or "Z"
        direction : "+" or "-"
        """

    # ── Timing helpers ───────────────────────────────────────────────────────

    @abc.abstractmethod
    def micros(self) -> int:
        """Return microseconds since initialise() was called (like Arduino micros())."""

    @abc.abstractmethod
    def delay_us(self, microseconds: int) -> None:
        """Block for (at least) the given number of microseconds."""
