"""
Profile Mode Screen
===================
Wizard for multi-point profile/taper turning.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)
from ui.theme import CLR_ACCENT, CLR_TEXT_DIM
from core.state_manager import get_state

if TYPE_CHECKING:
    from modes.profile_mode import ProfileMode


class ProfileScreen(QWidget):
    exit_requested = pyqtSignal()

    _STEP_LABELS = {
        0:  "Touch tool to stock OD, press OK",
        4:  "Move X to retract position, press OK",
        7:  "Select number of profile points",
        10: "Move to profile point and press OK",
        20: "Set depth of cut (DOC), press OK",
        30: "Profile running...",
        40: "Profile complete!",
    }

    def __init__(self, mode: "ProfileMode", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._mode.register_step_changed(self._on_step_changed)
        self._build_ui()
        self._refresh()
        self._dro_timer = QTimer(self)
        self._dro_timer.timeout.connect(self._refresh_dro)
        self._dro_timer.start(100)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(8)

        hdr = QHBoxLayout()
        title = QLabel("△  Profile / Taper")
        title.setStyleSheet(
            f"color: {CLR_ACCENT}; font-size: 20px; font-weight: bold;"
        )
        self._point_lbl = QLabel("")
        self._point_lbl.setStyleSheet(f"color: {CLR_TEXT_DIM}; font-size: 14px;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._point_lbl)
        root.addLayout(hdr)

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

        self._prompt = QLabel("")
        self._prompt.setObjectName("wizard_prompt")
        root.addWidget(self._prompt)

        self._value_display = QLabel("")
        self._value_display.setObjectName("wizard_value")
        self._value_display.setAlignment(Qt.AlignCenter)
        root.addWidget(self._value_display)

        self._sub_info = QLabel("")
        self._sub_info.setAlignment(Qt.AlignCenter)
        self._sub_info.setStyleSheet(
            f"color: {CLR_TEXT_DIM}; font-size: 15px;"
        )
        root.addWidget(self._sub_info)
        root.addStretch()

        nav = QHBoxLayout()
        nav.setSpacing(8)
        self._btn_dec  = QPushButton("▼")
        self._btn_inc  = QPushButton("▲")
        self._btn_ok   = QPushButton("✓  OK")
        self._btn_exit = QPushButton("✕  EXIT")
        self._btn_exit.setStyleSheet("color: #ff1744; border-color: #ff1744;")
        for b in (self._btn_dec, self._btn_inc, self._btn_ok, self._btn_exit):
            b.setMinimumSize(130, 64)
            nav.addWidget(b)
        self._btn_dec.clicked.connect(self._mode.select_prev)
        self._btn_inc.clicked.connect(self._mode.select_next)
        self._btn_ok.clicked.connect(self._mode.confirm)
        self._btn_exit.clicked.connect(self._on_exit)
        root.addLayout(nav)

    def _on_step_changed(self, step: int) -> None:
        self._refresh()

    def _refresh(self) -> None:
        step = self._mode.step
        prompt = self._STEP_LABELS.get(step, "")
        self._prompt.setText(prompt)

        st = get_state()
        u  = st.unit_label()

        if step == 7:
            self._value_display.setText(
                f"{self._mode.setup.num_points} points"
            )
        elif step == 10:
            self._point_lbl.setText(self._mode.point_label)
            z_mm = st.z_display()
            x_mm = st.x_display()
            self._value_display.setText(
                f"X:{x_mm:+.4f}  Z:{z_mm:+.3f} {u}"
            )
        elif step == 20:
            self._value_display.setText(
                f"DOC = {self._mode.doc_mm:.3f} mm"
            )
            self._sub_info.setText(
                f"Total passes: {self._mode.setup.pass_total}"
            )
        elif step == 30:
            s = self._mode.setup
            self._value_display.setText(
                f"Pass {s.pass_current} / {s.pass_total}"
            )
        elif step == 40:
            self._value_display.setText("✓  DONE")

        nav_steps = {7, 20}
        self._btn_dec.setVisible(step in nav_steps)
        self._btn_inc.setVisible(step in nav_steps)
        self._btn_ok.setVisible(step not in {30, 40})

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
