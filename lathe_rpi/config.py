b"""
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
# NOTE: STEP/DIR verified against test/enc_drive_motor.py (validated on real
# hardware): X STEP=24, DIR=23.  Keep these in sync with that test.
GPIO_X_STEP   = 24
GPIO_X_DIR    = 23
GPIO_X_ENABLE = 25

# Buttons (active LOW – input pull-up)
GPIO_BTN_1    = 26
GPIO_BTN_2    = 20
GPIO_BTN_3    = 21

# Half-nut lever switch (active HIGH when engaged)
GPIO_HALFNUT  = 4

# Limit switches (active LOW = triggered, NO switch wired to GND, pull-up).
#
# Hardware fitted: ONE limit switch per axis.
#   * Z-axis limit  →  GPIO 16   (GPIO_LIM_Z_PLUS)
#   * X-axis limit  →  GPIO 8    (GPIO_LIM_X_PLUS)
# The MINUS pins below are reserved for a future second switch per axis and can
# be left unwired (they read "not triggered" thanks to the internal pull-up).
# A single switch on GPIO 16 / GPIO 8 therefore raises the whole-axis limit.
GPIO_LIM_Z_PLUS  = 16   # Z-axis limit switch
GPIO_LIM_Z_MINUS = 7    # reserved (unwired)
GPIO_LIM_X_PLUS  = 8    # X-axis limit switch
GPIO_LIM_X_MINUS = 11   # reserved (unwired)

# Master enable for limit switches.  Set to False for bench testing when no
# limit switches are wired – otherwise a floating / NC / triggered limit pin
# will silently block motion (e.g. a stuck Z limit blocks all Z jog).
# When False, all limit reads return "not triggered".
LIMITS_ENABLED   = True

# Limit switch contact type:
#   True  = Normally-Closed (NC) – closed (to GND) at rest, OPENS when hit.
#           This is fail-safe: a broken wire reads as "limit hit".
#   False = Normally-Open (NO)  – open at rest, CLOSES (to GND) when hit.
# The fitted switches on this machine are NC.
LIMIT_NORMALLY_CLOSED = True

# Audible alert when a limit switch is hit (best-effort; needs a working audio
# output on the Pi).  The on-screen red flashing warning always shows.
LIMIT_SOUND      = True
# WAV file played on a limit hit (relative to the project dir, or absolute).
# Regenerate with: python assets/sounds/generate_alarm.py
LIMIT_SOUND_FILE = "assets/sounds/limit_alarm.wav"
# While a limit stays hit, replay the alarm this often (seconds); 0 = play once.
LIMIT_SOUND_REPEAT_S = 2.0

# ADC (MCP3208 via SPI  –  or ADS1015/ADS1115 via I2C)
# The validated hardware (test/enc_drive_motor.py) uses an ADS1015 on A0.
ADC_BACKEND     = "ads1015"   # "mcp3208" | "ads1015" | "ads1115" | "mock"
ADC_POT_CHANNEL = 0           # channel on the ADC chip
POT_REF_VOLTAGE = 3.3         # pot reference voltage (5.0 if wired to 5V rail)

# ── Debug / diagnostics ─────────────────────────────────────────────────────
# When True the Pi 5 HAL emits debug logs (encoder/pot/step/button activity)
# so hardware wiring can be verified against the display.  Can also be enabled
# at runtime with the environment variable  LATHE_DEBUG_HAL=1
DEBUG_HAL       = True

# ── Logging ─────────────────────────────────────────────────────────────────
# Diagnostic logs can be sent to the terminal (console) and/or a rotating log
# file for later analysis.  Configure both independently here.
LOG_TO_CONSOLE  = True                 # echo logs to the terminal / stderr
LOG_TO_FILE     = True                 # also write logs to LOG_FILE
LOG_FILE        = "logs/lathe.log"     # path (relative to project dir) or absolute
LOG_LEVEL       = "DEBUG"               # "DEBUG" | "INFO" | "WARNING" | "ERROR"
                                       # (forced to DEBUG when DEBUG_HAL/env is on)
LOG_MAX_BYTES   = 8_000_000            # rotate the log file after ~8 MB
LOG_BACKUP_COUNT = 3                   # keep this many rotated log files

# ── Display ────────────────────────────────────────────────────────────────
DISPLAY_WIDTH   = 800
DISPLAY_HEIGHT  = 480
FULLSCREEN      = True        # True = fills touchscreen on RPi; use 'python main.py --windowed' for desktop
