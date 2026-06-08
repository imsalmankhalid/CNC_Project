"""
Tests for Standard Mode – button handling, memory, units, Z-stop.
"""

import time
import pytest
from modes.standard_mode import StandardMode
from core.state_manager import get_state


class TestStandardModeButtons:

    def _press_and_release(self, hw, btn: int, hold_s: float) -> None:
        """Helper: press button, wait hold_s, release."""
        hw.press_button(btn, True)
        time.sleep(hold_s)
        hw.press_button(btn, False)

    def test_enter_sets_mode_0(self, hw_state):
        hw, state = hw_state
        sm = StandardMode(hw)
        sm.enter()
        assert state.mode == 0

    def test_btn1_short_cycles_x_memory(self, hw_state):
        hw, state = hw_state
        sm = StandardMode(hw)
        sm.enter()
        assert state.active_mem_x == 0
        sm._handle_release(1, 0.2)   # short press
        assert state.active_mem_x == 1
        sm._handle_release(1, 0.2)
        assert state.active_mem_x == 2
        sm._handle_release(1, 0.2)
        assert state.active_mem_x == 0  # wraps back

    def test_btn1_long_zeros_x_axis(self, hw_state):
        hw, state = hw_state
        state.mtr_pos_x = 500
        sm = StandardMode(hw)
        sm.enter()
        sm._handle_release(1, 0.8)   # long press
        assert state.mem_offset_x[0] == 500, \
            "Long press B1 should store current mtr_pos_x as zero offset"

    def test_btn2_short_cycles_z_memory(self, hw_state):
        hw, state = hw_state
        sm = StandardMode(hw)
        sm.enter()
        sm._handle_release(2, 0.2)
        assert state.active_mem_z == 1

    def test_btn2_long_zeros_z_axis(self, hw_state):
        hw, state = hw_state
        state.mtr_pos_z = -1200
        sm = StandardMode(hw)
        sm.enter()
        sm._handle_release(2, 0.8)
        assert state.mem_offset_z[0] == -1200

    def test_btn3_short_toggles_units(self, hw_state):
        hw, state = hw_state
        sm = StandardMode(hw)
        sm.enter()
        assert state.unit_mm is True
        sm._handle_release(3, 0.2)
        assert state.unit_mm is False
        sm._handle_release(3, 0.2)
        assert state.unit_mm is True

    def test_btn3_medium_sets_zstop(self, hw_state):
        hw, state = hw_state
        state.mtr_pos_z = 350
        sm = StandardMode(hw)
        sm.enter()
        sm._handle_release(3, 0.9)   # medium hold (0.6–1.2 s)
        assert state.mem_stop_z[0] == 350, \
            "Medium B3 hold should set Z-stop to current Z position"

    def test_btn3_long_calls_mode_select(self, hw_state):
        hw, state = hw_state
        called = []
        sm = StandardMode(hw)
        sm.enter()
        sm.register_mode_select_callback(lambda: called.append(True))
        sm._handle_release(3, 2.5)   # long hold (>1.8 s)
        assert len(called) == 1, "Long B3 hold should invoke mode-select callback"


class TestMachineStateDisplay:
    """Verify MachineState display helpers produce correct values."""

    def test_z_display_mm_at_zero_offset(self, hw_state):
        hw, state = hw_state
        state.mtr_pos_z = 0
        state.mem_offset_z[0] = 0
        assert state.z_display_mm() == pytest.approx(0.0)

    def test_z_display_mm_with_offset(self, hw_state):
        hw, state = hw_state
        from config import Z_PITCH, Z_MTR_CNT_PER_REV
        import config as cfg
        # Move 1 full lead-screw revolution = Z_PITCH mm
        counts = Z_MTR_CNT_PER_REV
        state.mtr_pos_z = counts
        state.mem_offset_z[0] = 0
        expected_mm = counts * (Z_PITCH / Z_MTR_CNT_PER_REV)
        assert state.z_display_mm() == pytest.approx(expected_mm)

    def test_unit_label_mm(self, hw_state):
        hw, state = hw_state
        state.unit_mm = True
        assert state.unit_label() == "mm"

    def test_unit_label_inch(self, hw_state):
        hw, state = hw_state
        state.unit_mm = False
        assert state.unit_label() == "in"

    def test_x_display_inch(self, hw_state):
        hw, state = hw_state
        from config import X_PITCH, X_MTR_CNT_PER_REV
        state.mtr_pos_x = X_MTR_CNT_PER_REV
        state.mem_offset_x[0] = 0
        state.unit_mm = False
        mm_val = X_MTR_CNT_PER_REV * (X_PITCH / X_MTR_CNT_PER_REV)
        expected_inch = mm_val / 25.4
        assert state.x_display() == pytest.approx(expected_inch)
