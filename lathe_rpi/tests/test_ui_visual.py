"""
Visual UI Tests
===============
pytest-qt tests that launch the real MainWindow with a MockInterface,
inject simulated hardware inputs, and assert the DRO labels / UI state
update accordingly.

Run with:
    pytest tests/test_ui_visual.py -v

These tests open an actual Qt window for a fraction of a second, exercise
a specific input, then assert the displayed text changed correctly.
They do NOT require any hardware.
"""

from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from core.state_manager import reset_state
from hal.mock_interface import MockInterface
from ui.app import MainWindow
import config as cfg


# ── Shared fixture ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _windowed(monkeypatch):
    """Force windowed (non-fullscreen) mode for every test."""
    monkeypatch.setattr(cfg, "FULLSCREEN", False)


@pytest.fixture
def hw():
    """Fresh MockInterface with a clean MachineState."""
    reset_state()
    interface = MockInterface()
    interface.initialise()
    return interface


@pytest.fixture
def window(qtbot, hw):
    """
    MainWindow wired to a MockInterface.
    qtbot registers it so Qt tears it down after each test.
    """
    win = MainWindow(hw=hw)
    qtbot.addWidget(win)
    win.show()
    qtbot.waitExposed(win)
    return win


# ── Helper ────────────────────────────────────────────────────────────────────

def _dro_z_text(window) -> str:
    return window._main_screen._z_val.text()


def _dro_x_text(window) -> str:
    return window._main_screen._x_val.text()


def _rpm_text(window) -> str:
    return window._main_screen._rpm_val.text()


def _feed_text(window) -> str:
    return window._main_screen._feed_val.text()


def _mem_z_btn_text(window) -> str:
    return window._main_screen._btn_mem_z.text()


def _mem_x_btn_text(window) -> str:
    return window._main_screen._btn_mem_x.text()


def _zstop_text(window) -> str:
    return window._main_screen._zstop_display.text()


# ── DRO update tests ──────────────────────────────────────────────────────────

class TestDROUpdates:

    def test_z_dro_starts_at_zero(self, window, qtbot):
        """On startup the Z DRO shows +0.000."""
        qtbot.wait(120)   # allow first refresh cycle
        assert _dro_z_text(window) == "+0.000"

    def test_x_dro_starts_at_zero(self, window, qtbot):
        """On startup the X DRO shows +0.000 (mm mode uses 3 decimal places)."""
        qtbot.wait(120)
        assert _dro_x_text(window) == "+0.000"

    def test_z_dro_updates_when_state_changes(self, window, qtbot, hw):
        """
        Injecting motor counts into MachineState directly updates the Z DRO label.
        This verifies the 20 Hz refresh timer fires and reads the new value.
        """
        qtbot.wait(80)
        before = _dro_z_text(window)

        # Directly move the Z motor position (500 counts ≈ 3.125 mm at 5mm/800cnt)
        window._state.mtr_pos_z = 500

        qtbot.wait(120)   # wait for at least one 50ms refresh tick
        after = _dro_z_text(window)
        assert after != before, f"Z DRO did not change: still '{after}'"
        assert after.startswith("+"), f"Expected positive Z, got '{after}'"

    def test_x_dro_updates_when_state_changes(self, window, qtbot, hw):
        """Injecting X motor counts updates the X DRO label."""
        qtbot.wait(80)
        before = _dro_x_text(window)

        # 400 counts ≈ 1 mm at 2mm/800cnt
        window._state.mtr_pos_x = 400

        qtbot.wait(120)
        after = _dro_x_text(window)
        assert after != before, f"X DRO did not change: still '{after}'"

    def test_z_dro_negative_value(self, window, qtbot):
        """Negative motor position gives a negative Z display value."""
        window._state.mtr_pos_z = -800   # −5 mm
        qtbot.wait(120)
        text = _dro_z_text(window)
        assert text.startswith("-"), f"Expected negative Z, got '{text}'"

    def test_z_dro_value_is_correct_mm(self, window, qtbot):
        """800 motor counts == 5.000 mm for the default Z config (5mm pitch, 800cnt/rev)."""
        from config import Z_PITCH, Z_MTR_CNT_PER_REV
        window._state.mtr_pos_z = Z_MTR_CNT_PER_REV   # one full revolution
        qtbot.wait(120)
        text = _dro_z_text(window)
        # Should show +5.000 (or very close)
        value = float(text)   # Python float() accepts '+5.000' natively
        assert abs(value - Z_PITCH) < 0.001, f"Expected +{Z_PITCH}, got '{text}'"

    def test_x_dro_value_is_correct_mm(self, window, qtbot):
        """800 motor counts == 2.000 mm for the default X config (2mm pitch, 800cnt/rev)."""
        from config import X_PITCH, X_MTR_CNT_PER_REV
        window._state.mtr_pos_x = X_MTR_CNT_PER_REV
        qtbot.wait(120)
        text = _dro_x_text(window)
        value = float(text)
        assert abs(value - X_PITCH) < 0.001, f"Expected +{X_PITCH}, got '{text}'"

    def test_z_dro_updates_multiple_times(self, window, qtbot):
        """DRO label changes on each position update, not just the first."""
        readings = []
        for counts in (0, 400, 800, 1200, 800, 0):
            window._state.mtr_pos_z = counts
            qtbot.wait(100)
            readings.append(_dro_z_text(window))
        # At least 3 distinct values in the sequence
        assert len(set(readings)) >= 3, f"Too few distinct DRO readings: {readings}"


# ── Encoder → motion controller → DRO integration ────────────────────────────

class TestEncoderToDRO:

    def test_z_encoder_injection_moves_dro(self, window, qtbot, hw):
        """
        Injecting encoder counts via MockInterface → MotionController picks them up
        → MachineState.mtr_pos_z changes → DRO label changes.
        (Full pipeline test: encoder → motion thread → state → UI timer → label)
        """
        qtbot.wait(100)   # let motion thread start
        before = _dro_z_text(window)

        # Inject 2000 counts (one full handwheel revolution at 2000 CPR)
        hw.simulate_z_encoder(2000)
        qtbot.wait(400)   # allow motion thread + UI timer to propagate

        after = _dro_z_text(window)
        assert after != before, (
            f"Z DRO did not change after encoder injection. "
            f"Was '{before}', still '{after}'. "
            f"Z motor steps issued: {hw.z_steps_issued}"
        )
        # Motor should have issued steps
        assert hw.z_steps_issued > 0, "No motor steps were issued for encoder input"

    def test_x_encoder_injection_moves_dro(self, window, qtbot, hw):
        """Injecting X encoder counts propagates to the X DRO label."""
        qtbot.wait(100)
        before = _dro_x_text(window)

        hw.simulate_x_encoder(2000)
        qtbot.wait(400)

        after = _dro_x_text(window)
        assert after != before, (
            f"X DRO did not change after encoder injection. "
            f"Was '{before}', still '{after}'. "
            f"X motor steps issued: {hw.x_steps_issued}"
        )
        assert hw.x_steps_issued > 0

    def test_z_encoder_negative_gives_negative_dro(self, window, qtbot, hw):
        """Negative encoder rotation shows a negative Z DRO value."""
        qtbot.wait(100)
        hw.simulate_z_encoder(-2000)
        qtbot.wait(400)
        text = _dro_z_text(window)
        assert text.startswith("-"), f"Expected negative Z after reverse encoder, got '{text}'"

    def test_encoder_steps_accumulate(self, window, qtbot, hw):
        """Multiple encoder injections accumulate in the DRO."""
        qtbot.wait(100)
        hw.simulate_z_encoder(1000)
        qtbot.wait(200)
        mid = _dro_z_text(window)

        hw.simulate_z_encoder(1000)   # another 1000
        qtbot.wait(200)
        final = _dro_z_text(window)

        assert mid != final, f"Second encoder injection had no effect. mid='{mid}' final='{final}'"


# ── Spindle RPM display ───────────────────────────────────────────────────────

class TestSpindleRPM:

    def test_rpm_starts_at_zero(self, window, qtbot):
        qtbot.wait(120)
        assert _rpm_text(window) == "0000"

    def test_rpm_updates_after_spindle_pulses(self, window, qtbot, hw):
        """Firing spindle pulses via MockInterface updates the RPM display."""
        qtbot.wait(100)
        before = _rpm_text(window)

        # Fire pulses at ~1200 RPM (50ms per revolution)
        for _ in range(5):
            hw.fire_spindle_pulse()
            time.sleep(0.05)

        qtbot.wait(200)
        after = _rpm_text(window)
        assert after != before, f"RPM display did not change: still '{after}'"
        assert int(after) > 0, f"Expected RPM > 0, got '{after}'"

    def test_rpm_shows_approximately_correct_value(self, window, qtbot, hw):
        """At ~1200 RPM pulse rate the display should read near 1200."""
        qtbot.wait(100)
        target_rpm = 1200.0
        interval = 60.0 / target_rpm

        for _ in range(8):
            hw.fire_spindle_pulse()
            time.sleep(interval)

        qtbot.wait(300)
        rpm_displayed = int(_rpm_text(window))
        # Allow ±20% tolerance
        assert abs(rpm_displayed - target_rpm) < target_rpm * 0.20, (
            f"Expected ~{target_rpm} RPM, displayed {rpm_displayed}"
        )


# ── Feed rate display ─────────────────────────────────────────────────────────

class TestFeedRate:

    def test_feed_updates_with_pot(self, window, qtbot, hw):
        """Setting the mock pot value updates the IPM feed display."""
        qtbot.wait(80)

        # Set pot to maximum → expect maximum feed
        hw.set_pot_value(1023)
        qtbot.wait(300)   # feed calculator polls at 100ms
        high = _feed_text(window)

        # Set pot to minimum
        hw.set_pot_value(0)
        qtbot.wait(300)
        low = _feed_text(window)

        assert high != low, f"Feed rate did not change with pot. high='{high}' low='{low}'"
        assert float(high) > float(low), (
            f"Expected high pot > low pot feed. high='{high}' low='{low}'"
        )


# ── Button functionality ──────────────────────────────────────────────────────

class TestButtons:

    def test_mem_z_button_cycles_slot(self, window, qtbot):
        """Tapping MEM Z button cycles M1 → M2 → M3 → M1."""
        qtbot.wait(80)
        assert "M1" in _mem_z_btn_text(window)

        window._main_screen._btn_mem_z.click()
        qtbot.wait(80)
        assert "M2" in _mem_z_btn_text(window)

        window._main_screen._btn_mem_z.click()
        qtbot.wait(80)
        assert "M3" in _mem_z_btn_text(window)

        window._main_screen._btn_mem_z.click()
        qtbot.wait(80)
        assert "M1" in _mem_z_btn_text(window), "Should wrap back to M1"

    def test_mem_x_button_cycles_slot(self, window, qtbot):
        """Tapping MEM X button cycles M1 → M2 → M3 → M1."""
        qtbot.wait(80)
        assert "M1" in _mem_x_btn_text(window)
        window._main_screen._btn_mem_x.click()
        qtbot.wait(80)
        assert "M2" in _mem_x_btn_text(window)
        window._main_screen._btn_mem_x.click()
        qtbot.wait(80)
        assert "M3" in _mem_x_btn_text(window)

    def test_zero_z_resets_dro_to_zero(self, window, qtbot):
        """ZERO Z button resets Z DRO to 0.000 from a non-zero position."""
        window._state.mtr_pos_z = 1600   # some position
        qtbot.wait(120)
        assert _dro_z_text(window) != "+0.000"

        window._main_screen._btn_zero_z.click()
        qtbot.wait(120)
        assert _dro_z_text(window) == "+0.000", (
            f"Z DRO should read +0.000 after ZERO Z, got '{_dro_z_text(window)}'"
        )

    def test_zero_x_resets_dro_to_zero(self, window, qtbot):
        """ZERO X button resets X DRO to 0.000 (mm mode, 3 decimal places)."""
        window._state.mtr_pos_x = 800
        qtbot.wait(120)
        window._main_screen._btn_zero_x.click()
        qtbot.wait(120)
        assert _dro_x_text(window) == "+0.000"

    def test_unit_toggle_changes_label(self, window, qtbot):
        """mm/in button toggles unit label on the DRO."""
        qtbot.wait(80)
        # Initially mm
        assert window._state.unit_mm is True

        window._main_screen._btn_unit.click()
        qtbot.wait(80)
        assert window._state.unit_mm is False
        assert window._main_screen._x_unit_lbl.text() == "in"

        window._main_screen._btn_unit.click()
        qtbot.wait(80)
        assert window._state.unit_mm is True
        assert window._main_screen._x_unit_lbl.text() == "mm"

    def test_unit_toggle_changes_dro_precision(self, window, qtbot):
        """Switching to inch changes the DRO to 4 decimal places."""
        window._state.mtr_pos_z = 800
        qtbot.wait(120)
        mm_text = _dro_z_text(window)
        mm_decimals = len(mm_text.split(".")[-1])

        window._main_screen._btn_unit.click()
        qtbot.wait(120)
        in_text = _dro_z_text(window)
        in_decimals = len(in_text.split(".")[-1])

        assert mm_decimals == 3, f"Expected 3 decimal places in mm, got {mm_decimals}"
        assert in_decimals == 4, f"Expected 4 decimal places in inch, got {in_decimals}"

    def test_set_stop_records_current_z(self, window, qtbot):
        """SET STOP button records the current Z position as the stop target."""
        window._state.mtr_pos_z = 1200
        qtbot.wait(80)
        window._main_screen._btn_set_stop.click()
        qtbot.wait(120)

        st = window._state
        assert st.mem_stop_z[st.active_mem_z] == 1200
        stop_text = _zstop_text(window)
        assert stop_text != "Not Set", f"Z-STOP should show a value, got '{stop_text}'"

    def test_clr_stop_resets_to_not_set(self, window, qtbot):
        """CLR STOP clears the Z-stop back to 'Not Set'."""
        # First set a stop
        window._state.mtr_pos_z = 800
        window._main_screen._btn_set_stop.click()
        qtbot.wait(120)
        assert _zstop_text(window) != "Not Set"

        window._main_screen._btn_clr_stop.click()
        qtbot.wait(120)
        assert _zstop_text(window) == "Not Set"

    def test_estop_button_sets_flag(self, window, qtbot):
        """E-STOP button sets the estop flag in MachineState."""
        assert window._state.estop is False
        window._main_screen._btn_estop.click()
        qtbot.wait(80)
        assert window._state.estop is True

    def test_estop_button_text_changes(self, window, qtbot):
        """E-STOP button text changes to reset message when engaged."""
        window._main_screen._btn_estop.click()
        qtbot.wait(80)
        assert "RESET" in window._main_screen._btn_estop.text()

    def test_estop_second_click_resets(self, window, qtbot):
        """Second tap on E-STOP resets the flag (normal operation resumed)."""
        window._main_screen._btn_estop.click()
        qtbot.wait(80)
        assert window._state.estop is True

        window._main_screen._btn_estop.click()
        qtbot.wait(80)
        assert window._state.estop is False


# ── Navigation tests ──────────────────────────────────────────────────────────

class TestNavigation:

    def test_modes_button_shows_mode_select(self, window, qtbot):
        """MODES button switches to the mode selection screen (index 1)."""
        qtbot.wait(80)
        assert window._stack.currentIndex() == MainWindow.IDX_MAIN

        window._main_screen._btn_modes.click()
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MODESEL

    def test_back_from_mode_select_returns_to_main(self, window, qtbot):
        """← Back on mode select returns to main DRO (index 0)."""
        window._main_screen._btn_modes.click()
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MODESEL

        mode_screen = window._mode_sel_screen
        # The ← Back button emits mode_selected(-1)
        mode_screen.mode_selected.emit(-1)
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MAIN

    def test_thread_mode_button_shows_thread_screen(self, window, qtbot):
        """Selecting Thread Cutting from mode select shows threading screen."""
        window._main_screen._btn_modes.click()
        qtbot.wait(100)
        window._mode_sel_screen.mode_selected.emit(1)
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_THREAD

    def test_profile_mode_button_shows_profile_screen(self, window, qtbot):
        """Selecting Profile mode shows the profile screen."""
        window._main_screen._btn_modes.click()
        qtbot.wait(100)
        window._mode_sel_screen.mode_selected.emit(3)
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_PROFILE

    def test_radius_mode_button_shows_radius_screen(self, window, qtbot):
        """Selecting Radius mode shows the radius screen."""
        window._main_screen._btn_modes.click()
        qtbot.wait(100)
        window._mode_sel_screen.mode_selected.emit(4)
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_RADIUS

    def test_exit_from_thread_returns_to_main(self, window, qtbot):
        """EXIT in threading screen returns to main DRO."""
        window._mode_sel_screen.mode_selected.emit(1)
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_THREAD

        window._thread_screen._btn_exit.click()
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MAIN

    def test_exit_from_profile_returns_to_main(self, window, qtbot):
        """EXIT in profile screen returns to main DRO."""
        window._mode_sel_screen.mode_selected.emit(3)
        qtbot.wait(100)
        window._profile_screen._btn_exit.click()
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MAIN

    def test_exit_from_radius_returns_to_main(self, window, qtbot):
        """EXIT in radius screen returns to main DRO."""
        window._mode_sel_screen.mode_selected.emit(4)
        qtbot.wait(100)
        window._radius_screen._btn_exit.click()
        qtbot.wait(100)
        assert window._stack.currentIndex() == MainWindow.IDX_MAIN


# ── Limit switch display ──────────────────────────────────────────────────────

class TestLimitSwitches:

    def test_limit_indicators_start_ok(self, window, qtbot):
        """All limit indicators start as '◉' (OK / not triggered)."""
        qtbot.wait(120)
        for lbl in (window._main_screen._lim_zp, window._main_screen._lim_zm,
                    window._main_screen._lim_xp, window._main_screen._lim_xm):
            assert "◉" in lbl.text(), f"Expected ◉ in '{lbl.text()}'"

    def test_z_plus_limit_triggered_changes_indicator(self, window, qtbot, hw):
        """Triggering Z+ limit switch changes its indicator to ⬛."""
        qtbot.wait(120)
        hw.trigger_limit("Z", "+", True)
        qtbot.wait(120)
        assert "⬛" in window._main_screen._lim_zp.text(), (
            f"Z+ indicator not showing triggered. Text: '{window._main_screen._lim_zp.text()}'"
        )

    def test_z_plus_limit_cleared_restores_indicator(self, window, qtbot, hw):
        """Clearing a triggered limit restores the ◉ indicator."""
        hw.trigger_limit("Z", "+", True)
        qtbot.wait(120)
        hw.trigger_limit("Z", "+", False)
        qtbot.wait(120)
        assert "◉" in window._main_screen._lim_zp.text()


# ── Memory slot isolation ─────────────────────────────────────────────────────

class TestMemorySlots:

    def test_each_memory_slot_has_independent_zero(self, window, qtbot):
        """M1, M2, M3 each store independent zero references."""
        st = window._state

        # Set zero in M1 at position 800
        st.mtr_pos_z = 800
        st.active_mem_z = 0
        window._main_screen._btn_zero_z.click()
        qtbot.wait(80)

        # Set zero in M2 at position 1600
        st.mtr_pos_z = 1600
        st.active_mem_z = 1
        window._main_screen._btn_zero_z.click()
        qtbot.wait(80)

        # Verify M1 offset stored 800, M2 stored 1600
        assert st.mem_offset_z[0] == 800
        assert st.mem_offset_z[1] == 1600

        # Switch to M1, DRO should show 0 when position = 800
        st.active_mem_z = 0
        st.mtr_pos_z = 800
        qtbot.wait(120)
        assert _dro_z_text(window) == "+0.000"

        # Switch to M2, DRO should show 0 when position = 1600
        st.active_mem_z = 1
        st.mtr_pos_z = 1600
        qtbot.wait(120)
        assert _dro_z_text(window) == "+0.000"

    def test_memory_slot_badge_updates_on_cycle(self, window, qtbot):
        """The M1/M2/M3 badge next to the DRO value updates when slot cycles."""
        qtbot.wait(80)
        assert window._main_screen._z_mem.text() == "M1"

        window._main_screen._btn_mem_z.click()
        qtbot.wait(80)
        assert window._main_screen._z_mem.text() == "M2"
