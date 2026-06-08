"""
Mock Hardware Interface – used for desktop testing and simulation.

Provides fully controllable, in-process state that tests can drive directly
without any GPIO hardware.  Keeps a complete history of z_step / x_step calls
so motion logic can be asserted in unit tests.
"""

from __future__ import annotations

import time
from typing import Callable, List

from .hardware_interface import HardwareInterface


class MockInterface(HardwareInterface):
    """
    Deterministic, in-process replacement for real GPIO hardware.

    All state is public so tests can seed inputs and inspect outputs.
    """

    def __init__(self) -> None:
        self._start_time_ns: int = 0

        # Encoder state
        self._z_enc: int = 0
        self._x_enc: int = 0

        # Motor step accumulator (total counts issued, signed)
        self.z_steps_issued: int = 0
        self.x_steps_issued: int = 0

        # Step history for detailed assertions
        self.z_step_history: List[int] = []
        self.x_step_history: List[int] = []

        # Motor enable state
        self.z_enabled: bool = True
        self.x_enabled: bool = True

        # Spindle
        self._spindle_callback: Callable[[], None] | None = None

        # Potentiometer 0–1023
        self._pot_value: int = 512

        # Buttons pressed state (key: 1/2/3  →  True/False)
        self._buttons: dict[int, bool] = {1: False, 2: False, 3: False}

        # Half-nut lever
        self._halfnut: bool = False

        # Limit switches {("X","+"): False, ("X","-"): False, ...}
        self._limits: dict[tuple[str, str], bool] = {
            ("Z", "+"): False,
            ("Z", "-"): False,
            ("X", "+"): False,
            ("X", "-"): False,
        }

    # ── Life-cycle ──────────────────────────────────────────────────────────

    def initialise(self) -> None:
        self._start_time_ns = time.monotonic_ns()

    def shutdown(self) -> None:
        pass

    # ── Encoders ────────────────────────────────────────────────────────────

    def get_z_encoder(self) -> int:
        return self._z_enc

    def set_z_encoder(self, value: int) -> None:
        self._z_enc = value

    def get_x_encoder(self) -> int:
        return self._x_enc

    def set_x_encoder(self, value: int) -> None:
        self._x_enc = value

    # ── Test helpers: simulate encoder rotation ──────────────────────────────

    def simulate_z_encoder(self, delta: int) -> None:
        """Add *delta* counts to the Z encoder (simulates HW rotation)."""
        self._z_enc += delta

    def simulate_x_encoder(self, delta: int) -> None:
        self._x_enc += delta

    # ── Servos ──────────────────────────────────────────────────────────────

    def z_step(self, counts: int) -> None:
        self.z_steps_issued += counts
        self.z_step_history.append(counts)

    def x_step(self, counts: int) -> None:
        self.x_steps_issued += counts
        self.x_step_history.append(counts)

    def enable_z_motor(self, enabled: bool) -> None:
        self.z_enabled = enabled

    def enable_x_motor(self, enabled: bool) -> None:
        self.x_enabled = enabled

    # ── Spindle ─────────────────────────────────────────────────────────────

    def register_spindle_callback(self, cb: Callable[[], None]) -> None:
        self._spindle_callback = cb

    def fire_spindle_pulse(self) -> None:
        """Test helper – trigger one spindle index pulse."""
        if self._spindle_callback:
            self._spindle_callback()

    # ── Potentiometer ────────────────────────────────────────────────────────

    def read_potentiometer(self) -> int:
        return self._pot_value

    def set_pot_value(self, value: int) -> None:
        """Test helper – set raw ADC reading (0–1023)."""
        self._pot_value = max(0, min(1023, value))

    # ── Digital inputs ──────────────────────────────────────────────────────

    def read_button(self, btn_id: int) -> bool:
        return self._buttons.get(btn_id, False)

    def press_button(self, btn_id: int, pressed: bool = True) -> None:
        """Test helper – simulate button press/release."""
        self._buttons[btn_id] = pressed

    def read_halfnut(self) -> bool:
        return self._halfnut

    def set_halfnut(self, engaged: bool) -> None:
        """Test helper – simulate half-nut lever."""
        self._halfnut = engaged

    def read_limit_switch(self, axis: str, direction: str) -> bool:
        return self._limits.get((axis, direction), False)

    def trigger_limit(self, axis: str, direction: str, triggered: bool = True) -> None:
        """Test helper – trigger a limit switch."""
        self._limits[(axis, direction)] = triggered

    # ── Timing helpers ───────────────────────────────────────────────────────

    def micros(self) -> int:
        elapsed_ns = time.monotonic_ns() - self._start_time_ns
        return elapsed_ns // 1000

    def delay_us(self, microseconds: int) -> None:
        if microseconds > 0:
            time.sleep(microseconds / 1_000_000)
