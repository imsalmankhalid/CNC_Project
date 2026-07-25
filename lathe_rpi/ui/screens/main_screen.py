"""
Main DRO Screen
===============
The primary operating screen shown in Standard (mode 0) operation.

Layout (800 × 480):
┌─────────────────────────────────────────────────────────────────────┐
│  [X]  +000.0000 mm  M1  │  RPM  1200  │  Z-STOP  Not Set          │
│  [Z]  -000.000  mm  M3  │  IPM   12.5  │  ●●●● limit indicators   │
├─────────────────────────────────────────────────────────────────────┤
│  [ZERO X]  [ZERO Z]  [UNIT mm/in]  [SET STOP]  [MODES]  [E-STOP]  │
└─────────────────────────────────────────────────────────────────────┘

The DRO values update via a QTimer at 20 Hz from MachineState.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from ui.theme import (
    CLR_ACCENT, CLR_AMBER, CLR_GREEN, CLR_RED,
    CLR_TEXT_DIM, STYLESHEET,
)
from core.state_manager import get_state

if TYPE_CHECKING:
    from modes.standard_mode import StandardMode


class DroValueLabel(QLabel):
    """Large monospaced DRO value display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dro_value")
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setMinimumWidth(320)


class MainScreen(QWidget):
    """Primary DRO screen for standard handwheel operation."""

    def __init__(self, standard_mode: "StandardMode", parent=None):
        super().__init__(parent)
        self._std = standard_mode
        self._state = get_state()

        # Limit-alarm state
        self._alarm_phase = 0            # flash phase counter
        self._prev_limit_z = False       # rising-edge detection for sound
        self._prev_limit_x = False

        self._build_ui()

        # Refresh DRO at 20 Hz
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(50)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 4)
        root.setSpacing(6)

        # ── Top strip: DRO + side panels ────────────────────────────────────
        top_strip = QHBoxLayout()
        top_strip.setSpacing(8)

        top_strip.addWidget(self._build_dro_panel(), stretch=6)
        top_strip.addWidget(self._build_speed_panel(), stretch=2)
        top_strip.addWidget(self._build_status_panel(), stretch=3)

        root.addLayout(top_strip, stretch=10)

        # ── Bottom button bar ────────────────────────────────────────────────
        root.addWidget(self._build_button_bar(), stretch=0)

        # ── Limit-hit warning banner (floating overlay, hidden by default) ───
        self._alarm_banner = QLabel("", self)
        self._alarm_banner.setObjectName("alarm_banner_on")
        self._alarm_banner.setAlignment(Qt.AlignCenter)
        self._alarm_banner.hide()

    def _position_alarm_banner(self) -> None:
        """Centre the warning banner near the top of the screen."""
        if not hasattr(self, "_alarm_banner"):
            return
        w = int(self.width() * 0.6)
        h = 60
        x = (self.width() - w) // 2
        y = 12
        self._alarm_banner.setGeometry(x, y, w, h)
        self._alarm_banner.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        super().resizeEvent(event)
        self._position_alarm_banner()

    def _make_card(self) -> QFrame:
        f = QFrame()
        f.setObjectName("card")
        return f

    def _build_dro_panel(self) -> QFrame:
        card = self._make_card()
        layout = QGridLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # X axis row
        x_axis = QLabel("X")
        x_axis.setObjectName("dro_axis_label")
        self._x_val = DroValueLabel()
        self._x_val.setText("+0.0000")
        x_unit = QLabel("mm")
        x_unit.setObjectName("dro_unit_label")
        self._x_mem = QLabel("M1")
        self._x_mem.setObjectName("dro_mem_label")
        self._x_mem.setAlignment(Qt.AlignCenter)

        layout.addWidget(x_axis,     0, 0, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._x_val, 0, 1, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(x_unit,     0, 2, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._x_mem, 0, 3, Qt.AlignCenter)

        # Horizontal divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep, 1, 0, 1, 4)

        # Z axis row
        z_axis = QLabel("Z")
        z_axis.setObjectName("dro_axis_label")
        self._z_val = DroValueLabel()
        self._z_val.setText("+0.000")
        z_unit = QLabel("mm")
        z_unit.setObjectName("dro_unit_label")
        self._z_mem = QLabel("M1")
        self._z_mem.setObjectName("dro_mem_label")
        self._z_mem.setAlignment(Qt.AlignCenter)

        layout.addWidget(z_axis,     2, 0, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._z_val, 2, 1, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(z_unit,     2, 2, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._z_mem, 2, 3, Qt.AlignCenter)

        layout.setColumnStretch(1, 10)
        self._x_unit_lbl = x_unit
        self._z_unit_lbl = z_unit

        return card

    def _build_speed_panel(self) -> QFrame:
        card = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(2)

        rpm_lbl = QLabel("RPM")
        rpm_lbl.setObjectName("panel_label")

        self._rpm_val = QLabel("0000")
        self._rpm_val.setObjectName("rpm_value")
        self._rpm_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)

        ipm_lbl = QLabel("IPM")
        ipm_lbl.setObjectName("panel_label")

        self._feed_val = QLabel("00.0")
        self._feed_val.setObjectName("feed_value")
        self._feed_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for w in (rpm_lbl, self._rpm_val, sep, ipm_lbl, self._feed_val):
            layout.addWidget(w)
        layout.addStretch()
        return card

    def _build_status_panel(self) -> QFrame:
        card = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        stop_lbl = QLabel("Z-STOP")
        stop_lbl.setObjectName("panel_label")
        layout.addWidget(stop_lbl)

        self._zstop_display = QLabel("Not Set")
        self._zstop_display.setObjectName("zstop_notset")
        self._zstop_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._zstop_display)

        layout.addSpacing(8)

        lim_lbl = QLabel("LIMITS")
        lim_lbl.setObjectName("panel_label")
        layout.addWidget(lim_lbl)

        lim_grid = QGridLayout()
        lim_grid.setSpacing(2)
        self._lim_zp = self._make_limit_dot("Z+")
        self._lim_zm = self._make_limit_dot("Z-")
        self._lim_xp = self._make_limit_dot("X+")
        self._lim_xm = self._make_limit_dot("X-")
        lim_grid.addWidget(self._lim_zp, 0, 0)
        lim_grid.addWidget(self._lim_zm, 0, 1)
        lim_grid.addWidget(self._lim_xp, 1, 0)
        lim_grid.addWidget(self._lim_xm, 1, 1)
        layout.addLayout(lim_grid)
        layout.addStretch()
        return card

    @staticmethod
    def _make_limit_dot(label: str) -> QLabel:
        lbl = QLabel(f"◉ {label}")
        lbl.setObjectName("limit_ok")
        return lbl

    def _build_button_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("mode_bar")
        # Height must clear the tallest button (E-STOP, 64px min) plus the 6px
        # top/bottom margins, otherwise the button overflows the bar and
        # overlaps the DRO area in fullscreen.
        bar.setFixedHeight(88)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)

        def btn(text: str, obj_name: str = "") -> QPushButton:
            b = QPushButton(text)
            b.setObjectName(obj_name or "mode_btn")
            return b

        self._btn_mem_x    = btn("X  M1 ▶")
        self._btn_zero_x   = btn("ZERO X")
        self._btn_mem_z    = btn("Z  M1 ▶")
        self._btn_zero_z   = btn("ZERO Z")
        self._btn_unit     = btn("mm / in")
        self._btn_set_stop = btn("SET STOP")
        self._btn_clr_stop = btn("CLR STOP")
        self._btn_modes    = btn("MODES ▶")
        self._btn_exit     = btn("✕ EXIT")
        self._btn_estop    = btn("⬛ E-STOP", "danger_btn")

        self._btn_mem_x.clicked.connect(self._on_mem_cycle_x)
        self._btn_zero_x.clicked.connect(self._on_zero_x)
        self._btn_mem_z.clicked.connect(self._on_mem_cycle_z)
        self._btn_zero_z.clicked.connect(self._on_zero_z)
        self._btn_unit.clicked.connect(self._on_toggle_unit)
        self._btn_set_stop.clicked.connect(self._on_set_stop)
        self._btn_clr_stop.clicked.connect(self._on_clr_stop)
        self._btn_modes.clicked.connect(self._on_modes)
        self._btn_exit.clicked.connect(self._on_exit)
        self._btn_estop.clicked.connect(self._on_estop)

        for b in (self._btn_mem_x, self._btn_zero_x,
                  self._btn_mem_z, self._btn_zero_z,
                  self._btn_unit, self._btn_set_stop,
                  self._btn_clr_stop, self._btn_modes):
            layout.addWidget(b, stretch=2)

        # Compact EXIT button (quit the app – useful on a fullscreen panel).
        self._btn_exit.setFixedWidth(70)
        layout.addWidget(self._btn_exit, stretch=0)

        layout.addSpacing(6)
        self._btn_estop.setMinimumWidth(130)
        layout.addWidget(self._btn_estop, stretch=0)

        return bar

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_mem_cycle_x(self) -> None:
        st = self._state
        st.active_mem_x = (st.active_mem_x + 1) % 3

    def _on_mem_cycle_z(self) -> None:
        st = self._state
        st.active_mem_z = (st.active_mem_z + 1) % 3

    def _on_zero_x(self) -> None:
        st = self._state
        st.mem_offset_x[st.active_mem_x] = st.mtr_pos_x

    def _on_zero_z(self) -> None:
        st = self._state
        st.mem_offset_z[st.active_mem_z] = st.mtr_pos_z

    def _on_toggle_unit(self) -> None:
        self._state.unit_mm = not self._state.unit_mm

    def _on_set_stop(self) -> None:
        st = self._state
        st.mem_stop_z[st.active_mem_z] = st.mtr_pos_z

    def _on_clr_stop(self) -> None:
        st = self._state
        st.mem_stop_z[st.active_mem_z] = 999_999

    def _on_modes(self) -> None:
        # show_mode_select is injected as an instance attribute by app.py
        show_fn = getattr(self, 'show_mode_select', None)
        if callable(show_fn):
            show_fn()

    def _on_exit(self) -> None:
        """Confirm, then quit the application (injected request_close callback)."""
        reply = QMessageBox.question(
            self,
            "Exit MbW Lathe",
            "Close the lathe control application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            close_fn = getattr(self, 'request_close', None)
            if callable(close_fn):
                close_fn()

    def _on_estop(self) -> None:
        st = self._state
        if st.estop:
            st.estop = False
            self._btn_estop.setText("⬛ E-STOP")
            self._btn_estop.setStyleSheet("")
        else:
            st.estop = True
            self._btn_estop.setText("⚠ RESET ESTOP")
            self._btn_estop.setStyleSheet(
                "background-color: #ff1744; color: white; border-color: #ff0000;"
            )

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        st = self._state
        unit = st.unit_label()
        prec = 3 if st.unit_mm else 4

        # X display
        x_disp = st.x_display()
        sign = "+" if x_disp >= 0 else ""
        self._x_val.setText(f"{sign}{x_disp:.{prec}f}")
        self._x_unit_lbl.setText(unit)
        self._x_mem.setText(f"M{st.active_mem_x + 1}")
        self._btn_mem_x.setText(f"X  M{st.active_mem_x + 1} \u25b6")

        # Z display
        z_disp = st.z_display()
        sign = "+" if z_disp >= 0 else ""
        self._z_val.setText(f"{sign}{z_disp:.{prec}f}")
        self._z_unit_lbl.setText(unit)
        self._z_mem.setText(f"M{st.active_mem_z + 1}")
        self._btn_mem_z.setText(f"Z  M{st.active_mem_z + 1} \u25b6")

        # RPM
        self._rpm_val.setText(f"{int(st.spindle_rpm):04d}")

        # Feed
        self._feed_val.setText(f"{st.feed_rate_ipm:4.1f}")

        # Z-STOP
        stop = st.mem_stop_z[st.active_mem_z]
        if stop >= 999_999:
            self._zstop_display.setText("Not Set")
            self._zstop_display.setObjectName("zstop_notset")
        else:
            from config import Z_PITCH, Z_MTR_CNT_PER_REV
            stop_mm = (stop - st.mem_offset_z[st.active_mem_z]) * (
                Z_PITCH / Z_MTR_CNT_PER_REV
            )
            stop_val = stop_mm if st.unit_mm else stop_mm / 25.4
            self._zstop_display.setText(f"{stop_val:+.3f} {unit}")
            self._zstop_display.setObjectName("zstop_set")
        self._zstop_display.style().unpolish(self._zstop_display)
        self._zstop_display.style().polish(self._zstop_display)

        # Limit indicators
        self._update_limit(self._lim_zp, st.limit_z_plus,  "Z+")
        self._update_limit(self._lim_zm, st.limit_z_minus, "Z-")
        self._update_limit(self._lim_xp, st.limit_x_plus,  "X+")
        self._update_limit(self._lim_xm, st.limit_x_minus, "X-")

        # Limit-hit alarm: red DRO box(es), flashing banner, and a beep.
        self._update_limit_alarm(st.limit_z, st.limit_x)

    # ── Limit-hit alarm ───────────────────────────────────────────────────────

    def _update_limit_alarm(self, limit_z: bool, limit_x: bool) -> None:
        # Colour the affected axis value box red.
        self._set_axis_alarm(self._z_val, limit_z)
        self._set_axis_alarm(self._x_val, limit_x)

        # Audible alert on the rising edge of either limit.
        if (limit_z and not self._prev_limit_z) or (limit_x and not self._prev_limit_x):
            self._play_alarm_sound()
        elif limit_z or limit_x:
            # Keep re-arming the alarm while a limit stays hit.
            self._maybe_repeat_alarm_sound()
        self._prev_limit_z = limit_z
        self._prev_limit_x = limit_x

        if not (limit_z or limit_x):
            if self._alarm_banner.isVisible():
                self._alarm_banner.hide()
            return

        # Compose the warning text.
        if limit_z and limit_x:
            msg = "\u26a0  Z & X LIMIT HIT  \u26a0"
        elif limit_z:
            msg = "\u26a0  Z-AXIS LIMIT HIT  \u26a0"
        else:
            msg = "\u26a0  X-AXIS LIMIT HIT  \u26a0"
        self._alarm_banner.setText(msg)

        # Flash: toggle style ~2.5 Hz (every 4 refresh ticks at 20 Hz).
        self._alarm_phase = (self._alarm_phase + 1) % 8
        on = self._alarm_phase < 4
        self._alarm_banner.setObjectName("alarm_banner_on" if on else "alarm_banner_off")
        self._alarm_banner.style().unpolish(self._alarm_banner)
        self._alarm_banner.style().polish(self._alarm_banner)
        if not self._alarm_banner.isVisible():
            self._position_alarm_banner()
            self._alarm_banner.show()
        self._alarm_banner.raise_()

    @staticmethod
    def _set_axis_alarm(lbl: QLabel, triggered: bool) -> None:
        want = "dro_value_alarm" if triggered else "dro_value"
        if lbl.objectName() != want:
            lbl.setObjectName(want)
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def _play_alarm_sound(self) -> None:
        """Play the limit alarm WAV (best-effort; falls back to a system beep)."""
        import time
        self._last_alarm_sound = time.monotonic()
        try:
            import config as cfg
            if not getattr(cfg, "LIMIT_SOUND", True):
                return
        except Exception:
            cfg = None

        wav = self._resolve_alarm_wav(cfg)
        if wav and self._spawn_wav_player(wav):
            return
        # Last-resort fallback.
        try:
            QApplication.beep()
        except Exception:
            pass

    def _maybe_repeat_alarm_sound(self) -> None:
        """Replay the alarm periodically while a limit remains hit."""
        import time
        try:
            import config as cfg
            if not getattr(cfg, "LIMIT_SOUND", True):
                return
            period = float(getattr(cfg, "LIMIT_SOUND_REPEAT_S", 0) or 0)
        except Exception:
            return
        if period <= 0:
            return
        last = getattr(self, "_last_alarm_sound", 0.0)
        if time.monotonic() - last >= period:
            self._play_alarm_sound()

    @staticmethod
    def _resolve_alarm_wav(cfg) -> str | None:
        import os
        rel = getattr(cfg, "LIMIT_SOUND_FILE", "assets/sounds/limit_alarm.wav") if cfg else \
            "assets/sounds/limit_alarm.wav"
        if os.path.isabs(rel):
            return rel if os.path.isfile(rel) else None
        # Project dir = two levels up from this file (ui/screens/ -> lathe_rpi/).
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, rel)
        return path if os.path.isfile(path) else None

    @staticmethod
    def _spawn_wav_player(wav: str) -> bool:
        """Start a non-blocking WAV playback via aplay or ffplay. Returns True on success."""
        import shutil
        import subprocess
        players = (
            ["aplay", "-q", wav],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", wav],
            ["paplay", wav],
        )
        for cmd in players:
            if shutil.which(cmd[0]):
                try:
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return True
                except Exception:
                    continue
        return False

    @staticmethod
    def _update_limit(lbl: QLabel, triggered: bool, name: str) -> None:
        if triggered:
            lbl.setText(f"⬛ {name}")
            lbl.setObjectName("limit_triggered")
        else:
            lbl.setText(f"◉ {name}")
            lbl.setObjectName("limit_ok")
        lbl.style().unpolish(lbl)
        lbl.style().polish(lbl)
