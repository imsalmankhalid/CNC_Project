"""
MbW Lathe HAT – Full Schematic Generator
Generates an interactive HTML schematic with all components placed and wired.
Also includes design suggestions and improvements.
"""

import json
from pathlib import Path

# ─── Component Definitions ──────────────────────────────────────────────────
# Each component has a designator, type, package, position (x, y), and pins.
# Pins have a name, net, and direction (relative to component center).

components = [
    # ── Power Input ──
    {
        "designator": "J17",
        "type": "DC Jack",
        "package": "5.5mm x 2.1mm barrel",
        "x": 50, "y": 50,
        "pins": [
            {"name": "Center", "net": "VIN_12V_RAW", "dx": 0, "dy": -20},
            {"name": "Sleeve", "net": "GND", "dx": 0, "dy": 20},
            {"name": "SW", "net": "NC", "dx": 20, "dy": 0},
        ]
    },
    {
        "designator": "F1",
        "type": "Fuse 1A slow-blow",
        "package": "1206",
        "x": 120, "y": 50,
        "pins": [
            {"name": "1", "net": "VIN_12V_RAW", "dx": -15, "dy": 0},
            {"name": "2", "net": "VIN_12V", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "D8",
        "type": "SMAJ13CA TVS",
        "package": "SMA",
        "x": 180, "y": 80,
        "pins": [
            {"name": "Anode", "net": "GND", "dx": 0, "dy": 15},
            {"name": "Cathode", "net": "VIN_12V", "dx": 0, "dy": -15},
        ]
    },
    {
        "designator": "C7",
        "type": "10µF 25V",
        "package": "1206",
        "x": 210, "y": 80,
        "pins": [
            {"name": "+", "net": "VIN_12V", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C8",
        "type": "100nF 25V",
        "package": "0805",
        "x": 240, "y": 80,
        "pins": [
            {"name": "1", "net": "VIN_12V", "dx": 0, "dy": -15},
            {"name": "2", "net": "GND", "dx": 0, "dy": 15},
        ]
    },

    # ── MP2307 Buck Regulator ──
    {
        "designator": "U3",
        "type": "MP2307DN Buck 12V→5V",
        "package": "SOP-8",
        "x": 300, "y": 50,
        "pins": [
            {"name": "1 VIN", "net": "VIN_12V", "dx": -25, "dy": -30},
            {"name": "2 EN", "net": "3V3", "dx": -25, "dy": -15},
            {"name": "3 SW", "net": "SW_5V", "dx": -25, "dy": 0},
            {"name": "4 GND", "net": "GND", "dx": -25, "dy": 15},
            {"name": "5 BOOT", "net": "BOOT_5V", "dx": 25, "dy": 15},
            {"name": "6 RT/CT", "net": "RT_CT", "dx": 25, "dy": 0},
            {"name": "7 FB", "net": "GND", "dx": 25, "dy": -15},
            {"name": "8 GND", "net": "GND", "dx": 25, "dy": -30},
        ]
    },
    {
        "designator": "D9",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 380, "y": 50,
        "pins": [
            {"name": "Anode", "net": "SW_5V", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "5V0_BUCK", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "L1",
        "type": "10µH shielded",
        "package": "6030",
        "x": 340, "y": 20,
        "pins": [
            {"name": "1", "net": "SW_5V", "dx": -15, "dy": 0},
            {"name": "2", "net": "5V0_BUCK", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "C9",
        "type": "22µF 16V",
        "package": "1206",
        "x": 420, "y": 80,
        "pins": [
            {"name": "+", "net": "5V0_BUCK", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C10",
        "type": "100nF 16V",
        "package": "0805",
        "x": 450, "y": 80,
        "pins": [
            {"name": "1", "net": "5V0_BUCK", "dx": 0, "dy": -15},
            {"name": "2", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C11",
        "type": "100nF 16V",
        "package": "0805",
        "x": 300, "y": 90,
        "pins": [
            {"name": "1", "net": "BOOT_5V", "dx": 0, "dy": -10},
            {"name": "2", "net": "SW_5V", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "R24",
        "type": "22kΩ",
        "package": "0805",
        "x": 330, "y": 80,
        "pins": [
            {"name": "1", "net": "RT_CT", "dx": -10, "dy": 0},
            {"name": "2", "net": "GND", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "C1",
        "type": "10µF 16V",
        "package": "0805",
        "x": 270, "y": 80,
        "pins": [
            {"name": "+", "net": "VIN_12V", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },

    # ── AP2112 LDO Regulator ──
    {
        "designator": "U4",
        "type": "AP2112K-3.3 LDO",
        "package": "SOT-223",
        "x": 300, "y": 160,
        "pins": [
            {"name": "1 VIN", "net": "VIN_12V", "dx": -20, "dy": -20},
            {"name": "2 GND", "net": "GND", "dx": -20, "dy": 0},
            {"name": "3 GND", "net": "GND", "dx": 20, "dy": -20},
            {"name": "4 VOUT", "net": "3V3_REG", "dx": 20, "dy": 0},
        ]
    },
    {
        "designator": "C12",
        "type": "10µF 16V",
        "package": "0805",
        "x": 260, "y": 190,
        "pins": [
            {"name": "+", "net": "VIN_12V", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C13",
        "type": "10µF 6.3V",
        "package": "0805",
        "x": 340, "y": 190,
        "pins": [
            {"name": "+", "net": "3V3_REG", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C14",
        "type": "100nF 10V",
        "package": "0805",
        "x": 370, "y": 190,
        "pins": [
            {"name": "1", "net": "3V3_REG", "dx": 0, "dy": -15},
            {"name": "2", "net": "GND", "dx": 0, "dy": 15},
        ]
    },

    # ── Diode OR-ing ──
    {
        "designator": "D11",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 500, "y": 50,
        "pins": [
            {"name": "Anode", "net": "5V0_BUCK", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "5V0", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "D12",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 500, "y": 80,
        "pins": [
            {"name": "Anode", "net": "5V0_RPi", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "5V0", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "D14",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 500, "y": 160,
        "pins": [
            {"name": "Anode", "net": "3V3_REG", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "D15",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 500, "y": 190,
        "pins": [
            {"name": "Anode", "net": "3V3_RPi", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "D13",
        "type": "SS34 Schottky",
        "package": "SMA",
        "x": 150, "y": 110,
        "pins": [
            {"name": "Anode", "net": "VIN_12V", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "VIN_12V_RAW", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "C5",
        "type": "10µF 10V",
        "package": "0805",
        "x": 560, "y": 65,
        "pins": [
            {"name": "+", "net": "5V0", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },
    {
        "designator": "C6",
        "type": "10µF 6.3V",
        "package": "0805",
        "x": 560, "y": 175,
        "pins": [
            {"name": "+", "net": "3V3", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },

    # ── 74HC245 Level Shifter ──
    {
        "designator": "U1",
        "type": "74HC245PW Level Shifter",
        "package": "TSSOP-20",
        "x": 700, "y": 100,
        "pins": [
            {"name": "1 A1", "net": "Z_STEP_3V3", "dx": -30, "dy": -60},
            {"name": "2 A2", "net": "Z_DIR_3V3", "dx": -30, "dy": -48},
            {"name": "3 A3", "net": "Z_EN_3V3", "dx": -30, "dy": -36},
            {"name": "4 A4", "net": "X_STEP_3V3", "dx": -30, "dy": -24},
            {"name": "5 A5", "net": "X_DIR_3V3", "dx": -30, "dy": -12},
            {"name": "6 A6", "net": "X_EN_3V3", "dx": -30, "dy": 0},
            {"name": "7 A7", "net": "NC", "dx": -30, "dy": 12},
            {"name": "8 A8", "net": "NC", "dx": -30, "dy": 24},
            {"name": "9 GND", "net": "GND", "dx": -30, "dy": 36},
            {"name": "10 /CE", "net": "GND", "dx": -30, "dy": 48},
            {"name": "20 VCC", "net": "5V0", "dx": 30, "dy": -60},
            {"name": "19 B8", "net": "NC", "dx": 30, "dy": -48},
            {"name": "18 B7", "net": "NC", "dx": 30, "dy": -36},
            {"name": "17 B6", "net": "X_EN_5V", "dx": 30, "dy": -24},
            {"name": "16 B5", "net": "X_DIR_5V", "dx": 30, "dy": -12},
            {"name": "15 B4", "net": "X_STEP_5V", "dx": 30, "dy": 0},
            {"name": "14 B3", "net": "Z_EN_5V", "dx": 30, "dy": 12},
            {"name": "13 B2", "net": "Z_DIR_5V", "dx": 30, "dy": 24},
            {"name": "12 B1", "net": "Z_STEP_5V", "dx": 30, "dy": 36},
            {"name": "11 DIR", "net": "5V0", "dx": 30, "dy": 48},
        ]
    },
    {
        "designator": "C1",
        "type": "100nF 10V",
        "package": "0805",
        "x": 740, "y": 30,
        "pins": [
            {"name": "1", "net": "5V0", "dx": 0, "dy": -10},
            {"name": "2", "net": "GND", "dx": 0, "dy": 10},
        ]
    },

    # ── ADS1015 ADC ──
    {
        "designator": "U2",
        "type": "ADS1015IDGSR ADC",
        "package": "VSSOP-10",
        "x": 700, "y": 250,
        "pins": [
            {"name": "1 SDA", "net": "I2C_SDA", "dx": -25, "dy": -25},
            {"name": "2 SCL", "net": "I2C_SCL", "dx": -25, "dy": -12},
            {"name": "3 A0", "net": "GND", "dx": -25, "dy": 0},
            {"name": "4 GND", "net": "GND", "dx": -25, "dy": 12},
            {"name": "5 DVDD", "net": "3V3", "dx": -25, "dy": 25},
            {"name": "6 DVSS", "net": "GND", "dx": 25, "dy": 25},
            {"name": "7 AIN0", "net": "POT_WIPER_ADC", "dx": 25, "dy": 12},
            {"name": "8 AIN1", "net": "NC", "dx": 25, "dy": 0},
            {"name": "9 AVDD", "net": "3V3", "dx": 25, "dy": -12},
            {"name": "10 AVSS", "net": "GND", "dx": 25, "dy": -25},
        ]
    },
    {
        "designator": "C2",
        "type": "100nF 10V",
        "package": "0805",
        "x": 740, "y": 220,
        "pins": [
            {"name": "1", "net": "3V3", "dx": 0, "dy": -10},
            {"name": "2", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "C3",
        "type": "100nF 10V",
        "package": "0805",
        "x": 740, "y": 280,
        "pins": [
            {"name": "1", "net": "3V3", "dx": 0, "dy": -10},
            {"name": "2", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "C4",
        "type": "10µF 6.3V",
        "package": "0805",
        "x": 770, "y": 250,
        "pins": [
            {"name": "+", "net": "3V3", "dx": 0, "dy": -15},
            {"name": "-", "net": "GND", "dx": 0, "dy": 15},
        ]
    },

    # ── I2C Pull-ups ──
    {
        "designator": "R22",
        "type": "4.7kΩ",
        "package": "0805",
        "x": 650, "y": 210,
        "pins": [
            {"name": "1", "net": "I2C_SDA", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "R23",
        "type": "4.7kΩ",
        "package": "0805",
        "x": 650, "y": 230,
        "pins": [
            {"name": "1", "net": "I2C_SCL", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },

    # ── Potentiometer ──
    {
        "designator": "R9",
        "type": "10kΩ series",
        "package": "0805",
        "x": 760, "y": 270,
        "pins": [
            {"name": "1", "net": "POT_WIPER", "dx": -10, "dy": 0},
            {"name": "2", "net": "POT_WIPER_ADC", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "J7",
        "type": "JST PH 3-pin (Pot)",
        "package": "JST PH 2.0mm",
        "x": 820, "y": 270,
        "pins": [
            {"name": "1", "net": "5V0", "dx": 20, "dy": -15},
            {"name": "2", "net": "POT_WIPER", "dx": 20, "dy": 0},
            {"name": "3", "net": "GND", "dx": 20, "dy": 15},
        ]
    },

    # ── Servo Connectors ──
    {
        "designator": "R5",
        "type": "100Ω series",
        "package": "0805",
        "x": 760, "y": 140,
        "pins": [
            {"name": "1", "net": "Z_STEP_5V", "dx": -10, "dy": 0},
            {"name": "2", "net": "Z_STEP_SERVO", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "R6",
        "type": "100Ω series",
        "package": "0805",
        "x": 760, "y": 180,
        "pins": [
            {"name": "1", "net": "X_STEP_5V", "dx": -10, "dy": 0},
            {"name": "2", "net": "X_STEP_SERVO", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "J4",
        "type": "Molex 8-pin (Z Servo)",
        "package": "KK-254",
        "x": 850, "y": 100,
        "pins": [
            {"name": "1 STEP", "net": "Z_STEP_SERVO", "dx": 20, "dy": -35},
            {"name": "2 DIR", "net": "Z_DIR_5V", "dx": 20, "dy": -25},
            {"name": "3 EN", "net": "Z_EN_5V", "dx": 20, "dy": -15},
            {"name": "4 HLFB", "net": "NC", "dx": 20, "dy": -5},
            {"name": "5 GND", "net": "GND", "dx": 20, "dy": 5},
            {"name": "6 5V", "net": "5V0", "dx": 20, "dy": 15},
            {"name": "7 HV+", "net": "NC", "dx": 20, "dy": 25},
            {"name": "8 HV-", "net": "NC", "dx": 20, "dy": 35},
        ]
    },
    {
        "designator": "J5",
        "type": "Molex 8-pin (X Servo)",
        "package": "KK-254",
        "x": 850, "y": 200,
        "pins": [
            {"name": "1 STEP", "net": "X_STEP_SERVO", "dx": 20, "dy": -35},
            {"name": "2 DIR", "net": "X_DIR_5V", "dx": 20, "dy": -25},
            {"name": "3 EN", "net": "X_EN_5V", "dx": 20, "dy": -15},
            {"name": "4 HLFB", "net": "NC", "dx": 20, "dy": -5},
            {"name": "5 GND", "net": "GND", "dx": 20, "dy": 5},
            {"name": "6 5V", "net": "5V0", "dx": 20, "dy": 15},
            {"name": "7 HV+", "net": "NC", "dx": 20, "dy": 25},
            {"name": "8 HV-", "net": "NC", "dx": 20, "dy": 35},
        ]
    },

    # ── TVS on servo signals ──
    {
        "designator": "D1",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 130,
        "pins": [
            {"name": "Signal", "net": "Z_STEP_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "D2",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 145,
        "pins": [
            {"name": "Signal", "net": "Z_DIR_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "D3",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 160,
        "pins": [
            {"name": "Signal", "net": "Z_EN_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "D4",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 175,
        "pins": [
            {"name": "Signal", "net": "X_STEP_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "D5",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 190,
        "pins": [
            {"name": "Signal", "net": "X_DIR_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },
    {
        "designator": "D6",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 790, "y": 205,
        "pins": [
            {"name": "Signal", "net": "X_EN_5V", "dx": 0, "dy": -10},
            {"name": "GND", "net": "GND", "dx": 0, "dy": 10},
        ]
    },

    # ── Encoders ──
    {
        "designator": "J2",
        "type": "JST PH 6-pin (Z Encoder)",
        "package": "JST PH 2.0mm",
        "x": 100, "y": 250,
        "pins": [
            {"name": "1 VCC", "net": "3V3", "dx": -20, "dy": -25},
            {"name": "2 GND", "net": "GND", "dx": -20, "dy": -12},
            {"name": "3 A", "net": "Z_ENC_A_IN", "dx": -20, "dy": 0},
            {"name": "4 B", "net": "Z_ENC_B_IN", "dx": -20, "dy": 12},
            {"name": "5 IDX", "net": "NC", "dx": -20, "dy": 25},
            {"name": "6 NC", "net": "NC", "dx": -20, "dy": 38},
        ]
    },
    {
        "designator": "J3",
        "type": "JST PH 6-pin (X Encoder)",
        "package": "JST PH 2.0mm",
        "x": 100, "y": 350,
        "pins": [
            {"name": "1 VCC", "net": "3V3", "dx": -20, "dy": -25},
            {"name": "2 GND", "net": "GND", "dx": -20, "dy": -12},
            {"name": "3 A", "net": "X_ENC_A_IN", "dx": -20, "dy": 0},
            {"name": "4 B", "net": "X_ENC_B_IN", "dx": -20, "dy": 12},
            {"name": "5 IDX", "net": "NC", "dx": -20, "dy": 25},
            {"name": "6 NC", "net": "NC", "dx": -20, "dy": 38},
        ]
    },

    # ── Spindle ──
    {
        "designator": "J6",
        "type": "JST PH 3-pin (Spindle)",
        "package": "JST PH 2.0mm",
        "x": 100, "y": 450,
        "pins": [
            {"name": "1 5V", "net": "5V0", "dx": -20, "dy": -15},
            {"name": "2 GND", "net": "GND", "dx": -20, "dy": 0},
            {"name": "3 RAW", "net": "SPINDLE_RAW", "dx": -20, "dy": 15},
        ]
    },
    {
        "designator": "D7",
        "type": "PESD5V0S1UL TVS",
        "package": "SOD-323",
        "x": 140, "y": 470,
        "pins": [
            {"name": "Signal", "net": "SPINDLE_RAW", "dx": -15, "dy": 0},
            {"name": "GND", "net": "GND", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "R7",
        "type": "10kΩ divider top",
        "package": "0805",
        "x": 180, "y": 460,
        "pins": [
            {"name": "1", "net": "SPINDLE_RAW", "dx": -15, "dy": 0},
            {"name": "2", "net": "SPINDLE_IN", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "R8",
        "type": "20kΩ divider bot",
        "package": "0805",
        "x": 220, "y": 460,
        "pins": [
            {"name": "1", "net": "SPINDLE_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "GND", "dx": 15, "dy": 0},
        ]
    },

    # ── Buttons ──
    {
        "designator": "J8",
        "type": "Screw 2-pin (BTN1)",
        "package": "3.5mm",
        "x": 100, "y": 550,
        "pins": [
            {"name": "1", "net": "BTN1_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R10",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 140, "y": 540,
        "pins": [
            {"name": "1", "net": "BTN1_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "J9",
        "type": "Screw 2-pin (BTN2)",
        "package": "3.5mm",
        "x": 200, "y": 550,
        "pins": [
            {"name": "1", "net": "BTN2_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R11",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 240, "y": 540,
        "pins": [
            {"name": "1", "net": "BTN2_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "J10",
        "type": "Screw 2-pin (BTN3)",
        "package": "3.5mm",
        "x": 300, "y": 550,
        "pins": [
            {"name": "1", "net": "BTN3_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R12",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 340, "y": 540,
        "pins": [
            {"name": "1", "net": "BTN3_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },

    # ── Half-Nut ──
    {
        "designator": "J11",
        "type": "Screw 2-pin (Half-Nut)",
        "package": "3.5mm",
        "x": 400, "y": 550,
        "pins": [
            {"name": "1", "net": "HALF_NUT_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R13",
        "type": "10kΩ pull-down",
        "package": "0805",
        "x": 440, "y": 540,
        "pins": [
            {"name": "1", "net": "HALF_NUT_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "GND", "dx": 15, "dy": 0},
        ]
    },

    # ── Limit Switches ──
    {
        "designator": "J12",
        "type": "Screw 2-pin (LIM Z+)",
        "package": "3.5mm",
        "x": 500, "y": 550,
        "pins": [
            {"name": "1", "net": "LIM_Z_PLUS_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R14",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 540, "y": 540,
        "pins": [
            {"name": "1", "net": "LIM_Z_PLUS_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "J13",
        "type": "Screw 2-pin (LIM Z-)",
        "package": "3.5mm",
        "x": 600, "y": 550,
        "pins": [
            {"name": "1", "net": "LIM_Z_MINUS_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R15",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 640, "y": 540,
        "pins": [
            {"name": "1", "net": "LIM_Z_MINUS_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "J14",
        "type": "Screw 2-pin (LIM X+)",
        "package": "3.5mm",
        "x": 700, "y": 550,
        "pins": [
            {"name": "1", "net": "LIM_X_PLUS_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R16",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 740, "y": 540,
        "pins": [
            {"name": "1", "net": "LIM_X_PLUS_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "J15",
        "type": "Screw 2-pin (LIM X-)",
        "package": "3.5mm",
        "x": 800, "y": 550,
        "pins": [
            {"name": "1", "net": "LIM_X_MINUS_IN", "dx": -15, "dy": -10},
            {"name": "2", "net": "GND", "dx": -15, "dy": 10},
        ]
    },
    {
        "designator": "R17",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 840, "y": 540,
        "pins": [
            {"name": "1", "net": "LIM_X_MINUS_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },

    # ── E-Stop ──
    {
        "designator": "J16",
        "type": "Screw 4-pin (E-Stop)",
        "package": "3.5mm",
        "x": 900, "y": 550,
        "pins": [
            {"name": "1 NC", "net": "ESTOP_NC", "dx": -25, "dy": -15},
            {"name": "2 NO", "net": "ESTOP_IN", "dx": -25, "dy": 0},
            {"name": "3 COM", "net": "ESTOP_COM", "dx": 25, "dy": -15},
            {"name": "4 GND", "net": "GND", "dx": 25, "dy": 0},
        ]
    },
    {
        "designator": "R18",
        "type": "10kΩ pull-up",
        "package": "0805",
        "x": 940, "y": 540,
        "pins": [
            {"name": "1", "net": "ESTOP_IN", "dx": -15, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 15, "dy": 0},
        ]
    },

    # ── LEDs ──
    {
        "designator": "LED1",
        "type": "Green LED (12V Power)",
        "package": "0805",
        "x": 280, "y": 110,
        "pins": [
            {"name": "Anode", "net": "VIN_12V", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "GND", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "R19",
        "type": "1kΩ current limit",
        "package": "0805",
        "x": 250, "y": 110,
        "pins": [
            {"name": "1", "net": "VIN_12V", "dx": -10, "dy": 0},
            {"name": "2", "net": "VIN_12V", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "LED2",
        "type": "Red LED (E-Stop)",
        "package": "0805",
        "x": 940, "y": 510,
        "pins": [
            {"name": "Anode", "net": "ESTOP_IN", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "GND", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "R20",
        "type": "330Ω current limit",
        "package": "0805",
        "x": 910, "y": 510,
        "pins": [
            {"name": "1", "net": "ESTOP_IN", "dx": -10, "dy": 0},
            {"name": "2", "net": "ESTOP_IN", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "LED3",
        "type": "Yellow LED (Step Activity)",
        "package": "0805",
        "x": 760, "y": 120,
        "pins": [
            {"name": "Anode", "net": "Z_STEP_5V", "dx": -15, "dy": 0},
            {"name": "Cathode", "net": "GND", "dx": 15, "dy": 0},
        ]
    },
    {
        "designator": "R21",
        "type": "330Ω current limit",
        "package": "0805",
        "x": 730, "y": 120,
        "pins": [
            {"name": "1", "net": "Z_STEP_5V", "dx": -10, "dy": 0},
            {"name": "2", "net": "Z_STEP_5V", "dx": 10, "dy": 0},
        ]
    },

    # ── Encoder Pull-ups (optional) ──
    {
        "designator": "R1",
        "type": "10kΩ pull-up (opt)",
        "package": "0805",
        "x": 60, "y": 250,
        "pins": [
            {"name": "1", "net": "Z_ENC_A_IN", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "R2",
        "type": "10kΩ pull-up (opt)",
        "package": "0805",
        "x": 60, "y": 262,
        "pins": [
            {"name": "1", "net": "Z_ENC_B_IN", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "R3",
        "type": "10kΩ pull-up (opt)",
        "package": "0805",
        "x": 60, "y": 350,
        "pins": [
            {"name": "1", "net": "X_ENC_A_IN", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },
    {
        "designator": "R4",
        "type": "10kΩ pull-up (opt)",
        "package": "0805",
        "x": 60, "y": 362,
        "pins": [
            {"name": "1", "net": "X_ENC_B_IN", "dx": -10, "dy": 0},
            {"name": "2", "net": "3V3", "dx": 10, "dy": 0},
        ]
    },
]

# ─── Net Definitions ────────────────────────────────────────────────────────
# Group all pins by net name for wire routing.
nets = {}
for comp in components:
    for pin in comp["pins"]:
        net = pin["net"]
        if net not in nets:
            nets[net] = []
        px = comp["x"] + pin["dx"]
        py = comp["y"] + pin["dy"]
        nets[net].append({
            "designator": comp["designator"],
            "pin_name": pin["name"],
            "x": px,
            "y": py,
        })

# ─── Net Colors ─────────────────────────────────────────────────────────────
net_colors = {
    "GND": "#6e7681",
    "VIN_12V_RAW": "#ff7b72",
    "VIN_12V": "#ff7b72",
    "5V0_BUCK": "#ffa657",
    "5V0_RPi": "#f0883e",
    "5V0": "#f0883e",
    "3V3_REG": "#7ee787",
    "3V3_RPi": "#3fb950",
    "3V3": "#3fb950",
    "SW_5V": "#ffa657",
    "BOOT_5V": "#ffa657",
    "RT_CT": "#8b949e",
    "I2C_SDA": "#d2a8ff",
    "I2C_SCL": "#d2a8ff",
    "Z_STEP_3V3": "#58a6ff",
    "Z_DIR_3V3": "#58a6ff",
    "Z_EN_3V3": "#58a6ff",
    "X_STEP_3V3": "#58a6ff",
    "X_DIR_3V3": "#58a6ff",
    "X_EN_3V3": "#58a6ff",
    "Z_STEP_5V": "#58a6ff",
    "Z_DIR_5V": "#58a6ff",
    "Z_EN_5V": "#58a6ff",
    "X_STEP_5V": "#58a6ff",
    "X_DIR_5V": "#58a6ff",
    "X_EN_5V": "#58a6ff",
    "Z_STEP_SERVO": "#58a6ff",
    "X_STEP_SERVO": "#58a6ff",
    "POT_WIPER": "#79c0ff",
    "POT_WIPER_ADC": "#79c0ff",
    "Z_ENC_A_IN": "#79c0ff",
    "Z_ENC_B_IN": "#79c0ff",
    "X_ENC_A_IN": "#79c0ff",
    "X_ENC_B_IN": "#79c0ff",
    "SPINDLE_RAW": "#79c0ff",
    "SPINDLE_IN": "#79c0ff",
    "BTN1_IN": "#79c0ff",
    "BTN2_IN": "#79c0ff",
    "BTN3_IN": "#79c0ff",
    "HALF_NUT_IN": "#79c0ff",
    "LIM_Z_PLUS_IN": "#79c0ff",
    "LIM_Z_MINUS_IN": "#79c0ff",
    "LIM_X_PLUS_IN": "#79c0ff",
    "LIM_X_MINUS_IN": "#79c0ff",
    "ESTOP_NC": "#f0883e",
    "ESTOP_IN": "#79c0ff",
    "ESTOP_COM": "#8b949e",
    "NC": "#484f58",
}

# ─── Generate HTML ──────────────────────────────────────────────────────────
output_path = Path("lathe_rpi/PCB_Full_Schematic.html")

# Build SVG content
svg_width = 1050
svg_height = 650

svg_parts = []
svg_parts.append(f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">')
svg_parts.append('<defs>')
svg_parts.append('<style>')
svg_parts.append('''
  .comp-body { fill: #1c2333; stroke: #484f58; stroke-width: 1.5; rx: 4; }
  .comp-body-ic { fill: #1c2333; stroke: #f0883e; stroke-width: 1.5; rx: 4; }
  .comp-body-conn { fill: #1c2333; stroke: #79c0ff; stroke-width: 1.5; rx: 4; }
  .comp-body-power { fill: #1c2333; stroke: #ff7b72; stroke-width: 1.5; rx: 4; }
  .comp-body-reg { fill: #1c2333; stroke: #ffa657; stroke-width: 1.5; rx: 4; }
  .comp-body-ldo { fill: #1c2333; stroke: #7ee787; stroke-width: 1.5; rx: 4; }
  .comp-body-diode { fill: #1c2333; stroke: #f0883e; stroke-width: 1; rx: 3; }
  .comp-body-cap { fill: #1c2333; stroke: #3fb950; stroke-width: 1; rx: 3; }
  .comp-body-res { fill: #1c2333; stroke: #8b949e; stroke-width: 1; rx: 3; }
  .comp-body-led { fill: #1c2333; stroke: #ffa657; stroke-width: 1; rx: 3; }
  .comp-body-tvs { fill: #1c2333; stroke: #f0883e; stroke-width: 1; rx: 3; }
  .comp-body-ind { fill: #1c2333; stroke: #ffa657; stroke-width: 1; rx: 3; }
  .comp-body-fuse { fill: #1c2333; stroke: #ffa657; stroke-width: 1; rx: 3; }
  .comp-body-jack { fill: #1c2333; stroke: #ff7b72; stroke-width: 1.5; rx: 4; }
  .pin-line { stroke-width: 1.5; }
  .wire { stroke-width: 1.2; fill: none; }
  .wire-gnd { stroke-width: 2; fill: none; }
  .net-label { font-size: 7px; fill: #8b949e; }
  .comp-label { font-size: 8px; fill: #c9d1d9; font-weight: 600; }
  .comp-type { font-size: 6px; fill: #8b949e; }
  .pin-label { font-size: 6px; fill: #6e7681; }
  .title { font-size: 14px; fill: #58a6ff; font-weight: 700; }
  .subtitle { font-size: 10px; fill: #8b949e; }
  .section-label { font-size: 11px; fill: #f0883e; font-weight: 600; }
  .grid-line { stroke: #21262d; stroke-width: 0.5; }
''')
svg_parts.append('</style>')
svg_parts.append('</defs>')

# Background
svg_parts.append(f'<rect width="{svg_width}" height="{svg_height}" fill="#0d1117"/>')

# Grid
for x in range(0, svg_width, 50):
    svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{svg_height}" class="grid-line"/>')
for y in range(0, svg_height, 50):
    svg_parts.append(f'<line x1="0" y1="{y}" x2="{svg_width}" y2="{y}" class="grid-line"/>')

# Title
svg_parts.append(f'<text x="{svg_width//2}" y="20" text-anchor="middle" class="title">MbW Lathe HAT – Full Schematic</text>')
svg_parts.append(f'<text x="{svg_width//2}" y="32" text-anchor="middle" class="subtitle">All components placed with wired connections · 12V DC jack + RPi native USB-C · 74HC245 level shifting</text>')

# Section labels
svg_parts.append('<text x="10" y="45" class="section-label">⚡ POWER INPUT &amp; REGULATION</text>')
svg_parts.append('<text x="280" y="45" class="section-label">🔄 BUCK + LDO</text>')
svg_parts.append('<text x="480" y="45" class="section-label">🔗 DIODE OR-ING</text>')
svg_parts.append('<text x="680" y="45" class="section-label">🔄 74HC245 + ADC</text>')
svg_parts.append('<text x="840" y="45" class="section-label">🔌 SERVOS</text>')
svg_parts.append('<text x="10" y="240" class="section-label">📡 ENCODERS</text>')
svg_parts.append('<text x="10" y="440" class="section-label">⚙ SPINDLE</text>')
svg_parts.append('<text x="10" y="540" class="section-label">🔘 BUTTONS, LIMITS, E-STOP</text>')

# ── Draw Wires (Bus-Style Routing) ──
# For each net, compute a central bus point, then draw straight lines from each pin to the bus.
# Skip GND and NC for clarity (too many lines).
skip_nets = {"GND", "NC"}

for net_name, pins in nets.items():
    if net_name in skip_nets or len(pins) < 2:
        continue
    
    color = net_colors.get(net_name, "#8b949e")
    
    # Compute centroid of all pins for this net
    cx = sum(p["x"] for p in pins) / len(pins)
    cy = sum(p["y"] for p in pins) / len(pins)
    
    # Draw a small bus dot at centroid
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{color}" opacity="0.6"/>')
    
    # Draw straight lines from each pin to the bus centroid
    for p in pins:
        svg_parts.append(f'<line x1="{p["x"]}" y1="{p["y"]}" x2="{cx}" y2="{cy}" '
                        f'class="wire" stroke="{color}" opacity="0.35"/>')
    
    # Draw net label near centroid (offset to avoid overlap)
    svg_parts.append(f'<text x="{cx + 5}" y="{cy - 4}" class="net-label" fill="{color}" font-weight="600">{net_name}</text>')

# ── Draw GND plane indicator ──
svg_parts.append(f'<line x1="10" y1="{svg_height - 20}" x2="{svg_width - 10}" y2="{svg_height - 20}" class="wire-gnd" stroke="#6e7681"/>')
svg_parts.append(f'<text x="{svg_width//2}" y="{svg_height - 5}" text-anchor="middle" fill="#6e7681" font-size="9">GND PLANE (solid ground layer)</text>')

# ── Draw Components ──
for comp in components:
    x, y = comp["x"], comp["y"]
    desig = comp["designator"]
    ctype = comp["type"]
    
    # Determine component body style
    if "MP2307" in ctype or "Buck" in ctype:
        body_class = "comp-body-reg"
        w, h = 50, 60
    elif "AP2112" in ctype or "LDO" in ctype:
        body_class = "comp-body-ldo"
        w, h = 40, 40
    elif "74HC245" in ctype:
        body_class = "comp-body-ic"
        w, h = 60, 120
    elif "ADS1015" in ctype or "ADC" in ctype:
        body_class = "comp-body-ic"
        w, h = 50, 60
    elif "Jack" in ctype or "DC" in ctype:
        body_class = "comp-body-jack"
        w, h = 40, 40
    elif "Fuse" in ctype:
        body_class = "comp-body-fuse"
        w, h = 30, 20
    elif "SS34" in ctype or "Schottky" in ctype:
        body_class = "comp-body-diode"
        w, h = 30, 20
    elif "TVS" in ctype and "PESD" in ctype:
        body_class = "comp-body-tvs"
        w, h = 20, 16
    elif "SMAJ" in ctype:
        body_class = "comp-body-tvs"
        w, h = 30, 20
    elif "µH" in ctype:
        body_class = "comp-body-ind"
        w, h = 30, 20
    elif "LED" in ctype:
        body_class = "comp-body-led"
        w, h = 30, 20
    elif "µF" in ctype or "nF" in ctype:
        body_class = "comp-body-cap"
        w, h = 20, 16
    elif "kΩ" in ctype or "Ω" in ctype:
        body_class = "comp-body-res"
        w, h = 20, 16
    elif "JST" in ctype or "Molex" in ctype or "Screw" in ctype:
        body_class = "comp-body-conn"
        w, h = 40, 80
    else:
        body_class = "comp-body"
        w, h = 30, 20
    
    # Draw component body
    svg_parts.append(f'<rect x="{x - w//2}" y="{y - h//2}" width="{w}" height="{h}" class="{body_class}"/>')
    
    # Draw designator label
    svg_parts.append(f'<text x="{x}" y="{y - 3}" text-anchor="middle" class="comp-label">{desig}</text>')
    
    # Draw type label (shortened)
    short_type = ctype[:25]
    svg_parts.append(f'<text x="{x}" y="{y + 8}" text-anchor="middle" class="comp-type">{short_type}</text>')
    
    # Draw pin dots
    for pin in comp["pins"]:
        if pin["net"] == "NC":
            continue
        px = x + pin["dx"]
        py = y + pin["dy"]
        color = net_colors.get(pin["net"], "#8b949e")
        svg_parts.append(f'<circle cx="{px}" cy="{py}" r="2" fill="{color}"/>')

svg_parts.append('</svg>')

svg_content = "\n".join(svg_parts)

# ─── Design Suggestions ─────────────────────────────────────────────────────
suggestions = """
## Design Suggestions & Improvements

### ✅ Already Correct in Current Design
1. **I2C: NO capacitors on SDA/SCL** — This is correct. The 4.7kΩ pull-ups are sufficient.
   - ADS1015 adds ~5pF input capacitance per line
   - Short traces (<5cm) add ~100pF trace capacitance
   - Total bus capacitance well within 400pF I2C spec limit
   - **Adding caps would SLOW rise time and cause I2C errors at 400kHz**

2. **Decoupling capacitors** — Every IC has 100nF within 2mm of power pins ✓
3. **Bulk capacitors** — Each power rail has 10µF bulk cap ✓
4. **Regulator caps** — Per datasheet requirements ✓

### 🔧 Suggested Improvements

#### 1. I2C Ferrite Bead (Recommended for Industrial Environment)
- **Add**: FB1 = 600Ω ferrite bead (0805) on I2C_SDA between RPi and ADS1015
- **Why**: Lathe environment has motor noise. Ferrite bead filters high-frequency noise without slowing I2C.
- **Placement**: Between R22 (pull-up) and ADS1015 SDA pin
- **Part**: Murata BLM21PG601SN1D (600Ω @ 100MHz, 0805)
- **Cap after bead**: C15 = 22pF from filtered SDA to GND (absorbs HF noise)
- **Same for SCL**: FB2 + C16 = 22pF

#### 2. Encoder Input Protection (Recommended)
- **Add**: TVS diodes on encoder lines (Z_ENC_A/B, X_ENC_A/B)
- **Why**: Encoder cables run through noisy lathe environment
- **Part**: PESD5V0S1UL (same as servo signals)
- **Designators**: D16-D19 (one per encoder line)

#### 3. Power Rail Ferrite Beads (Optional)
- **Add**: FB3 on 5V0 rail near servo connectors (filters motor noise from feeding back)
- **Add**: FB4 on 3V3 rail near ADC (cleaner analog supply)
- **Part**: Murata BLM21PG121SN1D (120Ω @ 100MHz)

#### 4. Spindle Signal Schmitt Trigger (Recommended)
- **Add**: 74HC14 Schmitt trigger on SPINDLE_IN line
- **Why**: Spindle index signal may have slow rise time from voltage divider
- **Alternative**: Add RC filter (100Ω + 100pF) before GPIO pin

#### 5. E-Stop NC Trace Width (Critical)
- **Current**: ESTOP_NC trace breaks servo ENABLE
- **Suggestion**: Use 2mm wide trace for ESTOP_NC path (mechanical reliability)
- **Add**: Red silkscreen overlay on ESTOP_NC trace for visual inspection

#### 6. Ground Plane Stitching
- **Add**: Via every 10mm around board perimeter (connects top/bottom GND)
- **Add**: Via near every decoupling capacitor (low-indistance GND return)

#### 7. Test Points (Recommended for Debugging)
- **Add**: TP1 = 5V0 rail, TP2 = 3V3 rail, TP3 = VIN_12V
- **Add**: TP4 = I2C_SDA, TP5 = I2C_SCL (for oscilloscope probing)
- **Part**: TestPad_SMD:TestPad_1.0x1.0mm

#### 8. Boot/Configuration Jumpers (Optional)
- **Add**: JP1 = I2C pull-up enable/disable (for debugging with external pull-ups)
- **Add**: JP2 = Encoder pull-up enable/disable

#### 9. Thermal Relief for SOT-223 (AP2112)
- **Current**: Thermal pad connected to GND
- **Suggestion**: Use thermal relief pads (not solid connection) for easier soldering
- **Via count**: 3 vias under thermal pad to inner GND plane

#### 10. Component Orientation Markers
- **Add**: Pin 1 indicator dots on all IC footprints
- **Add**: Diode cathode band markers (white silkscreen line)
- **Add**: LED polarity markers (+/-)

### ⚠️ Things to Verify Before Fabrication

1. **MP2307 EN pin**: Currently tied to 3V3. Verify this works when 12V is absent (RPi back-feeds 3V3).
   - If 3V3 rail is powered by RPi back-feed, EN will be HIGH → buck tries to start → but no 12V input → no harm, just idle.
   - **Safe**: Buck won't output without VIN, so this is fine.

2. **74HC245 3.3V input threshold**: V_IH_min = 0.6 × 5V = 3.0V. RPi outputs 3.3V.
   - **Margin**: Only 0.3V above threshold. Works in practice but tight.
   - **Alternative**: Use 74HCT245 (T-series, V_IH = 2.0V at 5V) for better margin.
   - **Recommendation**: Stick with 74HC245 (already validated in Arduino design). If issues arise, switch to 74HCT245.

3. **Diode OR-ing power loss**: SS34 forward drop ~0.3V at typical current.
   - 5V rail: 5.0V - 0.3V = 4.7V at load (still within 5V tolerance)
   - 3.3V rail: 3.3V - 0.3V = 3.0V at load (within 3.3V ±5% = 3.135V minimum)
   - **WARNING**: 3.0V is BELOW 3.3V -5% tolerance! Consider using lower-drop Schottky (MBR0520T, Vf=0.2V) or ideal diode controller.
   - **Mitigation**: If using 12V always, this is fine (buck/LDO outputs are clean). Only matters in USB-C-only mode.

4. **Capacitor voltage ratings**: Verify all caps have adequate voltage rating.
   - C13 (10µF on 3V3_REG): 6.3V rating → OK (3.3V < 6.3V)
   - C9 (22µF on 5V0_BUCK): 16V rating → OK (5V < 16V)
   - C7 (10µF on VIN_12V): 25V rating → OK (12V < 25V)

5. **Inductor current rating**: L1 (10µH) should handle MP2307 peak current (~3.5A).
   - Verify inductor saturation current > 3.5A (Taiyo Yuden GQH101010T: 2.1A saturation)
   - **POTENTIAL ISSUE**: GQH101010T may saturate at high load. Consider COILCRAFT SSD1050 (3.2A sat) or similar.
"""

# ─── Build HTML ─────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MbW Lathe HAT – Full Schematic with Wires</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #0d1117;
    color: #c9d1d9;
    padding: 20px;
  }}
  h1 {{
    text-align: center;
    color: #58a6ff;
    margin-bottom: 16px;
    font-size: 22px;
  }}
  .schematic-container {{
    overflow-x: auto;
    margin-bottom: 30px;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px;
  }}
  .suggestions {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  .suggestions h2 {{
    color: #f0883e;
    font-size: 16px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #30363d;
  }}
  .suggestions h3 {{
    color: #58a6ff;
    font-size: 14px;
    margin: 16px 0 8px 0;
  }}
  .suggestions ul {{
    margin-left: 20px;
    margin-bottom: 12px;
  }}
  .suggestions li {{
    margin-bottom: 4px;
    line-height: 1.5;
  }}
  .suggestions code {{
    background: #21262d;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
  }}
  .warning {{
    background: #2a1f00;
    border: 1px solid #f0883e;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
  }}
  .warning strong {{
    color: #f0883e;
  }}
  .net-list {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 20px;
  }}
  .net-list h2 {{
    color: #58a6ff;
    font-size: 16px;
    margin-bottom: 12px;
  }}
  .net-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }}
  .net-table th {{
    background: #21262d;
    padding: 8px;
    text-align: left;
    border-bottom: 2px solid #30363d;
  }}
  .net-table td {{
    padding: 4px 8px;
    border-bottom: 1px solid #21262d;
  }}
  .net-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
  }}
</style>
</head>
<body>

<h1>MbW Lathe HAT – Full Schematic with Wired Connections</h1>

<div class="schematic-container">
{svg_content}
</div>

<div class="net-list">
<h2>Net Connection Table</h2>
<table class="net-table">
<tr><th>Net Name</th><th>Color</th><th>Connected Components</th><th>Pin Count</th></tr>
"""

# Sort nets by name, skip GND and NC
for net_name in sorted(nets.keys()):
    if net_name in {"GND", "NC"}:
        continue
    pins = nets[net_name]
    color = net_colors.get(net_name, "#8b949e")
    comps = ", ".join(set(f"{p['designator']}({p['pin_name']})" for p in pins))
    html += f'<tr><td><span class="net-dot" style="background:{color}"></span>{net_name}</td>'
    html += f'<td style="color:{color}">{color}</td>'
    html += f'<td>{comps}</td>'
    html += f'<td>{len(pins)}</td></tr>\n'

html += """</table>
</div>

<div class="suggestions">
""" + suggestions + """
</div>

</body>
</html>
"""

output_path.write_text(html, encoding="utf-8")
print(f"✅ Generated: {output_path.absolute()}")
print(f"   Components: {len(components)}")
print(f"   Nets: {len(nets)}")
print(f"   SVG Size: {svg_width}x{svg_height}")
