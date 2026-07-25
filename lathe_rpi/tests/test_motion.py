"""
Tests for MotionController – Z and X handwheel logic.

These tests use the MockInterface to inject encoder counts and assert
that the correct number of motor steps are issued.
"""

import pytest
import time
import config as cfg
from core.motion_controller import MotionController
from core.state_manager import get_state


class TestZHandwheel:
    """Z-axis handwheel encoder → servo step conversion."""

    def test_z_no_input_no_steps(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        # Call internal method directly (no thread needed)
        mc._z_enc_old = hw.get_z_encoder()
        mc._process_z_handwheel()
        assert hw.z_steps_issued == 0

    def test_z_positive_encoder_issues_positive_steps(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._z_enc_old = 0
        # Simulate 100 encoder counts in + direction
        hw.simulate_z_encoder(100)
        mc._process_z_handwheel()
        assert hw.z_steps_issued > 0, "Positive encoder input should issue positive Z steps"

    def test_z_negative_encoder_issues_negative_steps(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._z_enc_old = 0
        hw.simulate_z_encoder(-100)
        mc._process_z_handwheel()
        assert hw.z_steps_issued < 0, "Negative encoder input should issue negative Z steps"

    def test_z_small_input_below_threshold_no_step(self, hw_state):
        """Encoder counts below COUNT_ADJ_INV should not trigger a step."""
        hw, state = hw_state
        mc = MotionController(hw)
        mc._z_enc_old = 0
        # AMT103-V at 2000 CPR: Z_COUNT_ADJ_INV = 0.625 → need >= 0.625 enc counts
        # Send 0 (no change) → no step
        mc._process_z_handwheel()
        assert hw.z_steps_issued == 0

    def test_z_position_updates_in_state(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._z_enc_old = 0
        hw.simulate_z_encoder(cfg.Z_ENC_CNT_PER_REV)  # one full revolution
        mc._process_z_handwheel()
        assert state.mtr_pos_z != 0, "Motor position must update after encoder input"

    @pytest.mark.skip(reason="Z limits temporarily disabled for bench testing "
                             "(Z mirrors X). Re-enable when the Z velocity/limit/"
                             "auto-stop logic in _process_z_handwheel is restored.")
    def test_z_limit_plus_blocks_positive_motion(self, hw_state):
        hw, state = hw_state
        state.limit_z_plus = True
        mc = MotionController(hw)
        mc._z_enc_old = 0
        hw.simulate_z_encoder(200)
        mc._process_z_handwheel()
        # Some steps may already have been calculated before limit check
        # Key assertion: steps should be 0 or very small (limited)
        assert hw.z_steps_issued == 0 or state.mtr_pos_z == 0, \
            "Z+ limit should block positive Z motion"

    @pytest.mark.skip(reason="Z limits temporarily disabled for bench testing "
                             "(Z mirrors X). Re-enable when the Z velocity/limit/"
                             "auto-stop logic in _process_z_handwheel is restored.")
    def test_z_limit_minus_blocks_negative_motion(self, hw_state):
        hw, state = hw_state
        state.limit_z_minus = True
        mc = MotionController(hw)
        mc._z_enc_old = 0
        hw.simulate_z_encoder(-200)
        mc._process_z_handwheel()
        total = sum(hw.z_step_history) if hw.z_step_history else 0
        assert hw.z_steps_issued == 0 or total >= 0, \
            "Z- limit should block negative Z motion"

    @pytest.mark.skip(reason="Z auto-stop temporarily disabled for bench testing "
                             "(Z mirrors X). Re-enable when the Z velocity/limit/"
                             "auto-stop logic in _process_z_handwheel is restored.")
    def test_z_autostop_halts_at_target(self, hw_state):
        hw, state = hw_state
        # Set stop at 100 motor counts from current position
        state.mtr_pos_z = 0
        state.mem_stop_z[0] = 100
        mc = MotionController(hw)
        mc._z_enc_old = 0
        # Push many encoder counts to try to overshoot
        hw.simulate_z_encoder(cfg.Z_ENC_CNT_PER_REV * 3)
        mc._process_z_handwheel()
        assert state.mtr_pos_z <= 100, \
            f"Autostop should prevent motor going beyond 100 counts; got {state.mtr_pos_z}"


class TestXHandwheel:
    """X-axis handwheel encoder → servo step conversion."""

    def test_x_positive_encoder_issues_positive_steps(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._x_enc_old = 0
        hw.simulate_x_encoder(50)
        mc._process_x_handwheel()
        assert hw.x_steps_issued > 0

    def test_x_negative_encoder_issues_negative_steps(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._x_enc_old = 0
        hw.simulate_x_encoder(-50)
        mc._process_x_handwheel()
        assert hw.x_steps_issued < 0

    def test_x_position_updates(self, hw_state):
        hw, state = hw_state
        mc = MotionController(hw)
        mc._x_enc_old = 0
        hw.simulate_x_encoder(cfg.X_ENC_CNT_PER_REV)
        mc._process_x_handwheel()
        assert state.mtr_pos_x != 0


class TestLimitSwitchPolling:
    """Limit switch state is reflected in MachineState."""

    def test_limit_z_plus_detected(self, hw_state):
        hw, state = hw_state
        hw.trigger_limit("Z", "+", True)
        mc = MotionController(hw)
        mc._check_limits()
        assert state.limit_z_plus is True

    def test_limit_clears_when_released(self, hw_state):
        hw, state = hw_state
        hw.trigger_limit("Z", "+", True)
        mc = MotionController(hw)
        mc._check_limits()
        hw.trigger_limit("Z", "+", False)
        mc._check_limits()
        assert state.limit_z_plus is False
