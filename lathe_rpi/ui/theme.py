"""
Industrial Dark Theme
=====================
PyQt5 stylesheet and colour constants for the MbW Lathe HMI.
Designed for readability on a 7-inch 800×480 touch panel in a workshop
environment (high-contrast, large touch targets, no small text).
"""

from PyQt5.QtGui import QColor, QFont

# ── Colour palette ────────────────────────────────────────────────────────────
CLR_BG          = "#0d0d0d"   # near-black background
CLR_PANEL       = "#1a1a1a"   # card / panel surface
CLR_BORDER      = "#2e2e2e"   # subtle panel border
CLR_ACCENT      = "#00c8ff"   # cyan accent (active values / highlights)
CLR_ACCENT_DIM  = "#007a9a"   # dim accent (inactive / labels)
CLR_GREEN       = "#00e676"   # status OK
CLR_AMBER       = "#ffab00"   # warning
CLR_RED         = "#ff1744"   # error / limit / estop
CLR_TEXT        = "#e0e0e0"   # primary text
CLR_TEXT_DIM    = "#757575"   # secondary / label text
CLR_BTN_NORMAL  = "#1e3a4a"   # button background (normal)
CLR_BTN_HOVER   = "#1e5070"   # button hover / pressed
CLR_BTN_ACTIVE  = "#00c8ff"   # button when toggled active
CLR_MODE_BAR    = "#111827"   # mode strip background

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_MONO_LARGE = QFont("JetBrains Mono, Consolas, Monospace", 48, QFont.Bold)
FONT_MONO_MED   = QFont("JetBrains Mono, Consolas, Monospace", 28, QFont.Bold)
FONT_MONO_SMALL = QFont("JetBrains Mono, Consolas, Monospace", 16)
FONT_LABEL      = QFont("Segoe UI, Helvetica, Arial", 13)
FONT_LABEL_SM   = QFont("Segoe UI, Helvetica, Arial", 11)
FONT_BTN        = QFont("Segoe UI, Helvetica, Arial", 14, QFont.Bold)

# ── Master stylesheet ─────────────────────────────────────────────────────────
STYLESHEET = f"""
QWidget {{
    background-color: {CLR_BG};
    color: {CLR_TEXT};
    font-family: "Segoe UI", Helvetica, Arial;
}}

/* ── DRO value labels ─── */
QLabel#dro_value {{
    color: {CLR_ACCENT};
    font-size: 48px;
    font-weight: bold;
    font-family: "JetBrains Mono", Consolas, Monospace;
    letter-spacing: 2px;
}}

QLabel#dro_value_dimmed {{
    color: {CLR_ACCENT_DIM};
    font-size: 48px;
    font-weight: bold;
    font-family: "JetBrains Mono", Consolas, Monospace;
}}

QLabel#dro_axis_label {{
    color: {CLR_TEXT_DIM};
    font-size: 20px;
    font-weight: bold;
    padding-right: 6px;
}}

QLabel#dro_unit_label {{
    color: {CLR_TEXT_DIM};
    font-size: 16px;
    padding-left: 4px;
}}

QLabel#dro_mem_label {{
    color: {CLR_ACCENT_DIM};
    font-size: 14px;
    border: 1px solid {CLR_ACCENT_DIM};
    border-radius: 4px;
    padding: 2px 6px;
    min-width: 30px;
    max-width: 40px;
}}

/* ── Speed / Feed panel ─── */
QLabel#rpm_value {{
    color: {CLR_GREEN};
    font-size: 32px;
    font-weight: bold;
    font-family: "JetBrains Mono", Consolas, Monospace;
}}

QLabel#feed_value {{
    color: {CLR_AMBER};
    font-size: 32px;
    font-weight: bold;
    font-family: "JetBrains Mono", Consolas, Monospace;
}}

QLabel#panel_label {{
    color: {CLR_TEXT_DIM};
    font-size: 13px;
}}

/* ── Cards / panels ─── */
QFrame#card {{
    background-color: {CLR_PANEL};
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
}}

/* ── Mode bar ─── */
QFrame#mode_bar {{
    background-color: {CLR_MODE_BAR};
    border-top: 1px solid {CLR_BORDER};
}}

/* ── Touchable buttons ─── */
QPushButton {{
    background-color: {CLR_BTN_NORMAL};
    color: {CLR_TEXT};
    border: 1px solid {CLR_BORDER};
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    min-height: 52px;
    padding: 0 12px;
}}

QPushButton:pressed {{
    background-color: {CLR_BTN_HOVER};
    border-color: {CLR_ACCENT};
}}

QPushButton:checked {{
    background-color: {CLR_BTN_ACTIVE};
    color: {CLR_BG};
    border-color: {CLR_ACCENT};
}}

QPushButton#mode_btn {{
    min-height: 56px;
    border-radius: 8px;
    font-size: 15px;
}}

QPushButton#danger_btn {{
    background-color: #3a0010;
    color: {CLR_RED};
    border-color: {CLR_RED};
    font-size: 18px;
    font-weight: bold;
    min-height: 64px;
}}

QPushButton#danger_btn:pressed {{
    background-color: {CLR_RED};
    color: white;
}}

/* ── Z-STOP status label ─── */
QLabel#zstop_set {{
    color: {CLR_ACCENT};
    font-size: 14px;
    font-family: "JetBrains Mono", Consolas;
    border: 1px solid {CLR_ACCENT_DIM};
    border-radius: 4px;
    padding: 3px 8px;
}}

QLabel#zstop_notset {{
    color: {CLR_TEXT_DIM};
    font-size: 14px;
    border: 1px solid {CLR_BORDER};
    border-radius: 4px;
    padding: 3px 8px;
}}

/* ── Limit / estop indicators ─── */
QLabel#limit_ok {{
    color: {CLR_GREEN};
    font-size: 12px;
}}

QLabel#limit_triggered {{
    color: {CLR_RED};
    font-size: 12px;
    font-weight: bold;
}}

/* ── Wizard screen prompt text ─── */
QLabel#wizard_prompt {{
    color: {CLR_TEXT};
    font-size: 20px;
    font-weight: bold;
    padding: 6px 0;
}}

QLabel#wizard_value {{
    color: {CLR_ACCENT};
    font-size: 32px;
    font-weight: bold;
    font-family: "JetBrains Mono", Consolas;
}}

/* ── Separator ─── */
QFrame[frameShape="4"] {{
    color: {CLR_BORDER};
    margin: 4px 0;
}}

/* ── Scrollbar (if needed) ─── */
QScrollBar:vertical {{
    width: 8px;
    background: {CLR_PANEL};
}}

QScrollBar::handle:vertical {{
    background: {CLR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
"""
