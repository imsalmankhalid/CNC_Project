"""
Main Application Window
=======================
QStackedWidget containing all screens.  Owns the motion controller,
spindle monitor, and half-nut controller lifecycle.
Selects real vs. mock hardware backend based on platform detection.
"""

from __future__ import annotations

import sys
import platform

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
)

import config as cfg
from ui.theme import STYLESHEET
from ui.screens.main_screen import MainScreen
from ui.screens.mode_select_screen import ModeSelectScreen
from ui.screens.thread_screen import ThreadScreen
from ui.screens.profile_screen import ProfileScreen
from ui.screens.radius_screen import RadiusScreen

from core.state_manager import get_state
from core.motion_controller import MotionController
from core.spindle import SpindleMonitor
from core.halfnut import HalfNutController
from core.feed_calculator import FeedCalculator

from modes.standard_mode import StandardMode
from modes.threading_mode import ThreadingMode
from modes.profile_mode import ProfileMode
from modes.radius_mode import RadiusMode


def _create_hardware():
    """Return the appropriate HAL back-end for the current platform."""
    is_rpi = (
        platform.system() == "Linux"
        and platform.machine().startswith(("arm", "aarch"))
    )
    if is_rpi:
        # Auto-enable fullscreen on RPi unless already overridden
        if cfg.FULLSCREEN is False and "--windowed" not in sys.argv:
            cfg.FULLSCREEN = True
        try:
            from hal.rpi_interface import RpiInterface
            hw = RpiInterface()
            hw.initialise()
            return hw
        except Exception as exc:
            print(f"[WARN] RPi pigpio interface init failed ({exc}) – trying RPi5/gpiozero interface")
            try:
                from hal.rpi5_interface import Rpi5Interface
                hw = Rpi5Interface()
                hw.initialise()
                return hw
            except Exception as exc5:
                print(f"[WARN] RPi5 gpiozero interface init failed ({exc5}) – falling back to mock")

    from hal.mock_interface import MockInterface
    hw = MockInterface()
    hw.initialise()
    return hw


class MainWindow(QMainWindow):
    """Top-level window for the MbW Lathe HMI."""

    # Screen index constants
    IDX_MAIN    = 0
    IDX_MODESEL = 1
    IDX_THREAD  = 2
    IDX_PROFILE = 3
    IDX_RADIUS  = 4

    def __init__(self, hw=None) -> None:
        super().__init__()
        self.setWindowTitle("MbW Lathe Control System")
        self.setStyleSheet(STYLESHEET)

        if cfg.FULLSCREEN:
            self.showFullScreen()
        else:
            self.resize(cfg.DISPLAY_WIDTH, cfg.DISPLAY_HEIGHT)

        # Hardware – accept injected interface (for testing/demo) or auto-detect
        self._hw = hw if hw is not None else _create_hardware()

        # Core services
        self._state    = get_state()
        self._motion   = MotionController(self._hw)
        self._spindle  = SpindleMonitor(self._hw)
        self._halfnut  = HalfNutController(self._hw)
        self._feed_calc = FeedCalculator(self._hw)

        # Modes
        self._std_mode     = StandardMode(self._hw)
        self._thread_mode  = ThreadingMode(self._hw)
        self._profile_mode = ProfileMode(self._hw)
        self._radius_mode  = RadiusMode(self._hw)

        # Screens
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._main_screen    = MainScreen(self._std_mode)
        self._mode_sel_screen = ModeSelectScreen()
        self._thread_screen  = ThreadScreen(self._thread_mode)
        self._profile_screen = ProfileScreen(self._profile_mode)
        self._radius_screen  = RadiusScreen(self._radius_mode)

        self._stack.addWidget(self._main_screen)     # 0
        self._stack.addWidget(self._mode_sel_screen) # 1
        self._stack.addWidget(self._thread_screen)   # 2
        self._stack.addWidget(self._profile_screen)  # 3
        self._stack.addWidget(self._radius_screen)   # 4

        # Wire navigation
        self._std_mode.register_mode_select_callback(self.show_mode_select)
        self._main_screen.show_mode_select = self.show_mode_select   # type: ignore[attr-defined]
        self._mode_sel_screen.mode_selected.connect(self._on_mode_selected)
        self._thread_screen.exit_requested.connect(self._return_to_main)
        self._profile_screen.exit_requested.connect(self._return_to_main)
        self._radius_screen.exit_requested.connect(self._return_to_main)

        # Start core services
        self._spindle.start()
        self._motion.start()
        self._feed_calc.start()
        self._std_mode.enter()

        # Half-nut poll timer (10 ms)
        self._hn_timer = QTimer(self)
        self._hn_timer.timeout.connect(self._halfnut.poll)
        self._hn_timer.start(10)

        # Standard mode tick timer (50 ms)
        self._std_timer = QTimer(self)
        self._std_timer.timeout.connect(self._std_mode.tick)
        self._std_timer.start(50)

        self._stack.setCurrentIndex(self.IDX_MAIN)

    # ── Navigation ────────────────────────────────────────────────────────────

    def show_mode_select(self) -> None:
        self._stack.setCurrentIndex(self.IDX_MODESEL)

    def _return_to_main(self) -> None:
        self._std_mode.enter()
        self._stack.setCurrentIndex(self.IDX_MAIN)

    def _on_mode_selected(self, mode_id: int) -> None:
        if mode_id == -1 or mode_id == 0:
            self._return_to_main()
            return
        if mode_id == 1:
            self._thread_mode.enter()
            self._stack.setCurrentIndex(self.IDX_THREAD)
        elif mode_id == 3:
            self._profile_mode.enter()
            self._stack.setCurrentIndex(self.IDX_PROFILE)
        elif mode_id == 4:
            self._radius_mode.enter()
            self._stack.setCurrentIndex(self.IDX_RADIUS)

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._hn_timer.stop()
        self._std_timer.stop()
        self._motion.stop()
        self._feed_calc.stop()
        try:
            self._hw.shutdown()
        except Exception:
            pass
        event.accept()


def run_app() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("MbW Lathe")

    # Hide cursor on RPi touchscreen
    if cfg.FULLSCREEN:
        app.setOverrideCursor(Qt.BlankCursor)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
