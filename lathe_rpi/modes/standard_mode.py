"""
Standard (DRO) Mode
===================
Normal handwheel operation with DRO display, Z-stop, memory management,
and unit toggle.  Corresponds to modeCt==0 in the Arduino code.

Button behaviour (ported from 01_Buttons.ino):
  Button 1  short  → cycle X memory slot (M1→M2→M3→M1)
  Button 1  long   → zero X at current position
  Button 2  short  → cycle Z memory slot
  Button 2  long   → zero Z at current position
  Button 3  short  → toggle mm ↔ inch
  Button 3  medium → set Z auto-stop to current position
  Button 3  long   → enter Mode selection
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, Optional

from .base_mode import BaseMode

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


class StandardMode(BaseMode):
    """DRO + handwheel mode."""

    # Button hold timing (seconds)
    _DEBOUNCE       = 0.04
    _SHORT_MAX      = 0.60
    _MEDIUM_MIN     = 0.60
    _MEDIUM_MAX     = 1.20
    _LONG_MIN       = 1.80

    def __init__(self, hw: "HardwareInterface") -> None:
        super().__init__(hw)
        self._btn_pressed_at: dict[int, float] = {1: 0.0, 2: 0.0, 3: 0.0}
        self._btn_was_down:   dict[int, bool]  = {1: False, 2: False, 3: False}
        self._on_enter_mode_select: Optional[Callable[[], None]] = None

    def register_mode_select_callback(self, cb: Callable[[], None]) -> None:
        """UI registers this to know when the user wants to enter mode selection."""
        self._on_enter_mode_select = cb

    # ── Life-cycle ────────────────────────────────────────────────────────────

    def enter(self) -> None:
        self._active = True
        self._state.mode = 0

    def exit(self) -> None:
        self._active = False

    # ── Main tick ─────────────────────────────────────────────────────────────

    def tick(self) -> None:
        if not self._active:
            return
        self._poll_buttons()

    # ── Button polling ────────────────────────────────────────────────────────

    def _poll_buttons(self) -> None:
        now = time.monotonic()
        for btn in (1, 2, 3):
            pressed = self._hw.read_button(btn)
            was_down = self._btn_was_down[btn]

            if pressed and not was_down:
                self._btn_pressed_at[btn] = now
                self._btn_was_down[btn] = True

            elif not pressed and was_down:
                held = now - self._btn_pressed_at[btn]
                if held >= self._DEBOUNCE:
                    self._handle_release(btn, held)
                self._btn_was_down[btn] = False

    def _handle_release(self, btn: int, held: float) -> None:
        st = self._state
        if btn == 1:
            if held <= self._SHORT_MAX:
                # Cycle X memory
                st.active_mem_x = (st.active_mem_x + 1) % 3
            else:
                # Zero X at current motor position
                st.mem_offset_x[st.active_mem_x] = st.mtr_pos_x

        elif btn == 2:
            if held <= self._SHORT_MAX:
                # Cycle Z memory + reset stop display
                st.active_mem_z = (st.active_mem_z + 1) % 3
                st.mem_stop_z[st.active_mem_z] = 999_999
            else:
                # Zero Z at current motor position
                st.mem_offset_z[st.active_mem_z] = st.mtr_pos_z
                st.mem_stop_z[st.active_mem_z] = 999_999

        elif btn == 3:
            if held <= self._SHORT_MAX:
                # Toggle units
                st.unit_mm = not st.unit_mm
            elif self._MEDIUM_MIN <= held <= self._MEDIUM_MAX:
                # Set Z auto-stop to current Z position
                st.mem_stop_z[st.active_mem_z] = st.mtr_pos_z
            elif held >= self._LONG_MIN:
                # Enter mode selection
                if self._on_enter_mode_select:
                    self._on_enter_mode_select()
