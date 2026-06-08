"""
Tests for Threading Mode – state machine progression.
"""

import pytest
from modes.threading_mode import ThreadingMode, THREAD_TABLE, MATERIAL_TABLE


class TestThreadingModeStateMachine:

    def test_initial_step_is_0(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        assert tm.step == 0

    def test_select_next_advances_size(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.select_next()
        assert tm.setup.size_idx == 1

    def test_select_prev_does_not_go_below_zero(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.select_prev()
        assert tm.setup.size_idx == 0

    def test_confirm_step0_advances_to_step2(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.confirm()
        assert tm.step == 2, "After confirming thread size, step should be 2 (material)"

    def test_confirm_step2_advances_to_step4(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.confirm()   # step 0 → 2
        tm.confirm()   # step 2 → 4
        assert tm.step == 4

    def test_current_thread_name_changes_with_selection(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        name0 = tm.current_thread_name
        tm.select_next()
        name1 = tm.current_thread_name
        assert name0 != name1

    def test_exit_resets_mode(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.confirm()
        tm.exit()
        assert not tm.active

    def test_step_changed_callback_fired(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        events = []
        tm.register_step_changed(lambda s: events.append(s))
        tm.confirm()
        assert len(events) >= 1

    def test_all_thread_table_entries_have_valid_pitch(self, hw_state):
        for entry in THREAD_TABLE:
            name, pitch_mm, od_mm, tol_mm = entry
            assert pitch_mm > 0, f"Thread {name} has invalid pitch"
            assert od_mm > 0

    def test_thread_param_calc_gives_valid_rpm(self, hw_state):
        hw, state = hw_state
        tm = ThreadingMode(hw)
        tm.enter()
        tm.setup.size_idx = 5   # 1/4"-20
        tm.setup.material_idx = 0  # Aluminum
        tm._calc_thread_params()
        import config as cfg
        assert cfg.SPNDL_RPM_MIN <= tm.setup.rpm_actual <= cfg.SPNDL_RPM_MAX
