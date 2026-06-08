"""
MbW Lathe System – Raspberry Pi Port
Machine Configuration  (mirrors the Arduino "User Variables" section)

Edit this file to match your specific lathe's mechanical parameters.
All distances in mm, angles in degrees, speeds in mm/min or RPM.
"""

# ── Z-Axis mechanics ────────────────────────────────────────────────────────
Z_MTR_PULLEY      = 28       # teeth on Z motor pulley
Z_SCR_PULLEY      = 28       # teeth on Z screw pulley
Z_SCR_PITCH       = 5.0      # Z lead-screw pitch (mm)
Z_HANDWHEEL       = 20.0     # Z linear motion (mm) per handwheel revolution
Z_ENC_CNT_PER_REV = 2000     # Z encoder counts / revolution  (4× if quadrature)
Z_MTR_CNT_PER_REV = 800      # Z motor counts / revolution  (set in ClearPath MSP)
Z_MAX_TRAVEL_MM   = 1000     # maximum travel range (mm)

# ── X-Axis mechanics ────────────────────────────────────────────────────────
X_MTR_PULLEY      = 24
X_SCR_PULLEY      = 24
X_SCR_PITCH       = 2.0
X_HANDWHEEL       = 2.0
X_ENC_CNT_PER_REV = 2000
X_MTR_CNT_PER_REV = 800

# ── Spindle limits ──────────────────────────────────────────────────────────
SPNDL_RPM_MAX     = 2060.0
SPNDL_RPM_MIN     = 240.0

# ── Feed-rate limits ────────────────────────────────────────────────────────
FEED_RATE_MIN_MM  = 12.7     # 0.5 IPM
FEED_RATE_MAX_MM  = 1270.0   # 50 IPM

# ── Threading parameters ────────────────────────────────────────────────────
THRD_C391         = 13.860   # C391 tool offset (mm)
THRD_ANG          = 27.5     # Modified thread infeed angle (deg)
THRD_AUTO_SPRING  = 2        # Number of automatic spring passes

# ── Motor timing constants ───────────────────────────────────────────────────
MTR_MIN_DELAY_US  = 600      # ClearPath minimum inter-step delay (µs)

# ── Derived Z constants (do not edit) ───────────────────────────────────────
Z_PITCH           = Z_SCR_PITCH * (Z_MTR_PULLEY / Z_SCR_PULLEY)
Z_COUNT_ADJUST    = (Z_HANDWHEEL / Z_ENC_CNT_PER_REV) / (Z_PITCH / Z_MTR_CNT_PER_REV)
Z_COUNT_ADJ_INV   = 1.0 / Z_COUNT_ADJUST   # enc counts per motor count
Z_MAX_MTR_CNT     = int(Z_MAX_TRAVEL_MM / (Z_PITCH / Z_MTR_CNT_PER_REV))

# ── Derived X constants (do not edit) ───────────────────────────────────────
X_PITCH           = X_SCR_PITCH * (X_MTR_PULLEY / X_SCR_PULLEY)
X_COUNT_ADJUST    = (X_HANDWHEEL / X_ENC_CNT_PER_REV) / (X_PITCH / X_MTR_CNT_PER_REV)
X_COUNT_ADJ_INV   = 1.0 / X_COUNT_ADJUST

# ── Handwheel velocity limits (mm/min) used for step-size banding ───────────
Z_VEL_LIMIT_A     = 20
Z_VEL_LIMIT_B     = 100
Z_VEL_LIMIT_C     = 800
Z_VEL_LIMIT_D     = 2000

Z_MAX_HW_VEL      = 5.0      # max physical HW rotation (rev/s)
Z_BUF_MULT        = 0.3      # buffer fraction  (~1/3 of enc counts/rev)
Z_MAX_ENC_BUF     = Z_BUF_MULT * Z_ENC_CNT_PER_REV
Z_MAX_VEL         = Z_MAX_HW_VEL * Z_HANDWHEEL * 60.0   # mm/min

# ── GPIO pin assignments (BCM numbering) ────────────────────────────────────
# Encoders (must be on interrupt-capable pins)
GPIO_Z_ENC_A  = 5
GPIO_Z_ENC_B  = 6
GPIO_X_ENC_A  = 13
GPIO_X_ENC_B  = 19

# Spindle index pulse
GPIO_SPINDLE  = 12

# Z-axis servo
GPIO_Z_STEP   = 17
GPIO_Z_DIR    = 27
GPIO_Z_ENABLE = 22

# X-axis servo
GPIO_X_STEP   = 23
GPIO_X_DIR    = 24
GPIO_X_ENABLE = 25

# Buttons (active LOW – input pull-up)
GPIO_BTN_1    = 26
GPIO_BTN_2    = 20
GPIO_BTN_3    = 21

# Half-nut lever switch (active HIGH when engaged)
GPIO_HALFNUT  = 4

# Limit switches (active LOW = triggered, NO wiring)
GPIO_LIM_Z_PLUS  = 16
GPIO_LIM_Z_MINUS = 7
GPIO_LIM_X_PLUS  = 8
GPIO_LIM_X_MINUS = 11

# ADC (MCP3208 via SPI  –  or ADS1115 via I2C)
ADC_BACKEND     = "ads1115"   # "mcp3208" | "ads1115" | "mock"
ADC_POT_CHANNEL = 0           # channel on the ADC chip

# ── Display ────────────────────────────────────────────────────────────────
DISPLAY_WIDTH   = 800
DISPLAY_HEIGHT  = 480
FULLSCREEN      = True        # True = fills touchscreen on RPi; use 'python main.py --windowed' for desktop
