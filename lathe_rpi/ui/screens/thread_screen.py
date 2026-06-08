"""
Threading Wizard Screen
=======================
Step-by-step thread cutting setup, mirroring the LCD prompts in 40_Thread.ino
but implemented as a modern full-screen wizard with large touch targets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.theme import CLR_ACCENT, CLR_AMBER, CLR_TEXT_DIM
from core.state_manager import get_state

if TYPE_CHECKING:
    from modes.threading_mode import ThreadingMode


class ThreadScreen(QWidget):
    """Touch wizard for external thread cutting setup and execution."""

    exit_requested = pyqtSignal()

    # Human-readable step descriptions (maps to mode.step values)
    _STEP_LABELS = {
        0:  ("Thread Size",      "Select thread size",              True),
        2:  ("Material",         "Select workpiece material",       True),
        4:  ("Cutting Tool",     "Select cutting tool material",    True),
        6:  ("Turn OD",          "Turn and measure stock OD",       False),
        8:  ("Set C391 Tool",    "Touch C391 gauge to OD, press OK", False),
        11: ("Set Tool Tip",     "Touch cutting tip to OD, press OK", False),
        20: ("Set X Retract",    "Move X to retract position, press OK", False),
        22: ("Set Z End",        "Move Z to thread end position, press OK", False),
        24: ("Set Z Start",      "Move Z to thread start position, press OK", False),
        30: ("Run Pass",         "Press RUN to execute next pass",  False),
        31: ("Pass Complete",    "Pass done – run again or finish", False),
    }

    def __init__(self, mode: "ThreadingMode", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._mode.register_step_changed(self._on_step_changed)
        self._build_ui()
        self._refresh()
        # Refresh live DRO at 10 Hz
        self._dro_timer = QTimer(self)
        self._dro_timer.timeout.connect(self._refresh_dro)
        self._dro_timer.start(100)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("⟨⟩  Thread Cutting")
        title.setStyleSheet(
            f"color: {CLR_ACCENT}; font-size: 20px; font-weight: bold;"
        )
        self._step_indicator = QLabel("Step 1 / 9")
        self._step_indicator.setStyleSheet(
            f"color: {CLR_TEXT_DIM}; font-size: 14px;"
        )
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._step_indicator)
        root.addLayout(header)

        # Live DRO strip
        dro_row = QHBoxLayout()
        self._live_x = QLabel("X: +0.0000 mm")
        self._live_x.setStyleSheet(
            f"color: {CLR_ACCENT}; font-family: Consolas, monospace; font-size: 16px; font-weight: bold;"
        )
        self._live_z = QLabel("Z: +0.000 mm")
        self._live_z.setStyleSheet(
            f"color: {CLR_ACCENT}; font-family: Consolas, monospace; font-size: 16px; font-weight: bold;"
        )
        dro_row.addWidget(self._live_x)
        dro_row.addStretch()
        dro_row.addWidget(self._live_z)
        root.addLayout(dro_row)

        # Prompt text
        self._prompt = QLabel("Select thread size")
        self._prompt.setObjectName("wizard_prompt")
        root.addWidget(self._prompt)

        # Value display (current selection or DRO echo)
        self._value_display = QLabel("")
        self._value_display.setObjectName("wizard_value")
        self._value_display.setAlignment(Qt.AlignCenter)
        root.addWidget(self._value_display)

        # Sub-info (recommended RPM, pitch, etc.)
        self._sub_info = QLabel("")
        self._sub_info.setAlignment(Qt.AlignCenter)
        self._sub_info.setStyleSheet(
            f"color: {CLR_TEXT_DIM}; font-size: 15px;"
        )
        root.addWidget(self._sub_info)

        root.addStretch()

        # Navigation buttons
        nav = QHBoxLayout()
        nav.setSpacing(8)

        self._btn_prev = QPushButton("▼  PREV")
        self._btn_next = QPushButton("▲  NEXT")
        self._btn_ok   = QPushButton("✓  ACCEPT")
        self._btn_run  = QPushButton("▶  RUN PASS")
        self._btn_run.setStyleSheet(
            f"background-color: #003320; color: #00e676; font-size: 16px;"
        )
        self._btn_exit = QPushButton("✕  EXIT")
        self._btn_exit.setStyleSheet(
            f"color: #ff1744; border-color: #ff1744;"
        )

        self._btn_prev.setMinimumSize(130, 64)
        self._btn_next.setMinimumSize(130, 64)
        self._btn_ok.setMinimumSize(160, 64)
        self._btn_run.setMinimumSize(160, 64)
        self._btn_exit.setMinimumSize(110, 64)

        self._btn_prev.clicked.connect(self._mode.select_prev)
        self._btn_next.clicked.connect(self._mode.select_next)
        self._btn_ok.clicked.connect(self._mode.confirm)
        self._btn_run.clicked.connect(self._mode.confirm)
        self._btn_exit.clicked.connect(self._on_exit)

        for w in (self._btn_prev, self._btn_next, self._btn_ok,
                  self._btn_run, self._btn_exit):
            nav.addWidget(w)

        root.addLayout(nav)

    # ── State updates ─────────────────────────────────────────────────────────

    def _on_step_changed(self, step: int) -> None:
        self._refresh()

    def _refresh(self) -> None:
        step = self._mode.step
        s    = self._mode.setup
        info = self._STEP_LABELS.get(step)

        if info:
            _title, prompt, has_nav = info
            self._prompt.setText(prompt)
            self._btn_prev.setVisible(has_nav)
            self._btn_next.setVisible(has_nav)
            self._btn_ok.setVisible(step not in (30, 31))
            self._btn_run.setVisible(step in (30, 31))

        # Update value display
        if step == 0:
            self._value_display.setText(self._mode.current_thread_name)
            self._sub_info.setText(
                f"Pitch: {self._mode.thread_pitch_mm:.3f} mm"
            )
        elif step == 2:
            self._value_display.setText(self._mode.current_material)
            self._sub_info.setText("")
        elif step == 4:
            self._value_display.setText(self._mode.current_tool)
            self._sub_info.setText("")
        elif step in (20, 22, 24):
            st = get_state()
            z_mm = st.z_display()
            x_mm = st.x_display()
            u = st.unit_label()
            self._value_display.setText(
                f"X: {x_mm:+.4f} {u}   Z: {z_mm:+.3f} {u}"
            )
            self._sub_info.setText("")
        elif step == 30:
            self._value_display.setText(f"Pass {s.pass_num + 1}")
            self._sub_info.setText(
                f"Rec. RPM: {s.rpm_actual:.0f}   Pitch: {self._mode.thread_pitch_mm:.3f} mm"
            )
        elif step == 31:
            self._value_display.setText(f"Pass {s.pass_num} complete")
            spring_rem = s.auto_spring - s.spring_count
            self._sub_info.setText(
                f"Spring passes remaining: {spring_rem}"
            )

        # Step counter (approximate)
        step_labels = list(self._STEP_LABELS.keys())
        if step in step_labels:
            idx = step_labels.index(step)
            self._step_indicator.setText(f"Step {idx + 1} / {len(step_labels)}")

    def _refresh_dro(self) -> None:
        st = get_state()
        u = st.unit_label()
        prec_x = 4 if st.unit_mm else 5
        prec_z = 3 if st.unit_mm else 4
        self._live_x.setText(f"X: {st.x_display():+.{prec_x}f} {u}")
        self._live_z.setText(f"Z: {st.z_display():+.{prec_z}f} {u}")

    def _on_exit(self) -> None:
        self._mode.exit()
        self.exit_requested.emit()
