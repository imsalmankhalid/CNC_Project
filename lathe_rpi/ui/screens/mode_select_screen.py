"""
Mode Selection Screen
=====================
Shown when the user taps MODES.  Touch-friendly grid of large mode buttons.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from ui.theme import CLR_ACCENT, CLR_TEXT_DIM


class ModeSelectScreen(QWidget):
    """Grid of large touch buttons to select an operating mode."""

    mode_selected = pyqtSignal(int)   # emits mode index (0/1/3/4)

    _MODES = [
        (0, "DRO\nHandwheel",    "◎"),
        (1, "Thread\nCutting",   "⟨⟩"),
        (3, "Profile\n/ Taper",  "△"),
        (4, "Radius\n/ Sphere",  "◔"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("Select Operating Mode")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {CLR_ACCENT}; font-size: 22px; font-weight: bold;"
        )
        root.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        for idx, (mode_id, label, icon) in enumerate(self._MODES):
            btn = QPushButton(f"{icon}\n{label}")
            btn.setObjectName("mode_btn")
            btn.setMinimumSize(160, 130)
            btn.setStyleSheet(
                "font-size: 18px; font-weight: bold; line-height: 1.4;"
            )
            btn.clicked.connect(lambda _checked, mid=mode_id: self.mode_selected.emit(mid))
            grid.addWidget(btn, idx // 2, idx % 2)

        root.addLayout(grid)

        back_btn = QPushButton("← Back")
        back_btn.setMinimumHeight(56)
        back_btn.clicked.connect(lambda: self.mode_selected.emit(-1))  # -1 = cancel
        root.addWidget(back_btn)
