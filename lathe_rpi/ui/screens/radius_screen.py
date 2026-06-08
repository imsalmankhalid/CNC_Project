"""
Radius / Sphere Screen
======================
Wizard for internal and external arc turning.
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
    from modes.radius_mode import RadiusMode


class RadiusScreen(QWidget):
    exit_requested = pyqtSignal()

    _STEP_LABELS = {
        0:  "Choose arc type",
        2:  "Choose insert type",
        4:  "Confirm insert size",
        7:  "Touch tool to known OD, press OK",
        10: "Move X to retract position, press OK",
        13: "Enter arc radius",
        16: "Touch tool to arc centre, press OK",
        20: "Set depth of cut, press OK",
        30: "Arc running...",
        40: "Arc complete!",
    }

    def __init__(self, mode: "RadiusMode", parent=None):
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

        title = QLabel("◔  Radius / Sphere")
        title.setStyleSheet(
            f"color: {CLR_ACCENT}; font-size: 20px; font-weight: bold;"
        )
        root.addWidget(title)

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
        self._prompt.setText(self._STEP_LABELS.get(step, ""))
        s  = self._mode.setup
        st = get_state()
        u  = st.unit_label()

        if step == 0:
            self._value_display.setText(self._mode.arc_type_label)
        elif step == 2:
            self._value_display.setText(self._mode.insert_type_label)
        elif step == 4:
            ins_val = s.insert_rad_mm * 2 if s.insert_type == 0 else s.insert_rad_mm
            self._value_display.setText(f"{ins_val:.3f} mm")
        elif step == 13:
            rad_val = s.arc_radius_mm if st.unit_mm else s.arc_radius_mm / 25.4
            self._value_display.setText(f"R = {rad_val:.2f} {u}")
        elif step == 20:
            doc = s.cut_depth_cnt * 2.0 / 800  # approx mm
            self._value_display.setText(f"DOC = {doc:.3f} mm")
            self._sub_info.setText(
                f"Total passes: {s.pass_total}"
            )
        elif step == 30:
            self._value_display.setText(
                f"Pass {s.pass_current} / {s.pass_total}"
            )
        elif step == 40:
            self._value_display.setText("✓  DONE")

        nav_steps = {0, 2, 13, 20}
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
