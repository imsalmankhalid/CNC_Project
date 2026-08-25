# MbW Lathe HAT – KiCad PCB Connection Reference

Complete pin-by-pin connection guide for designing the Raspberry Pi HAT PCB in KiCad.
All GPIO numbers use **BCM numbering**. RPi physical pin numbers are in parentheses.

**Level shifter:** 74HC245 (octal bus transceiver, directional A→B) — **not** TXB0108.
**Power:** 12 V DC adapter input on HAT. RPi powers itself via its **own native USB-C port** (not on HAT).
When 12V is absent, RPi USB-C back-feeds 5V/3.3V through GPIO header → HAT still works.

---

## Table of Contents

1. [Power Architecture](#1-power-architecture)
2. [12 V DC Input & Regulation](#2-12-v-dc-input--regulation)
3. [Power Diode OR-ing (12V regulators + RPi back-feed)](#3-power-diode-or-ing-12v-regulators--rpi-back-feed)
4. [Raspberry Pi 40-Pin GPIO Header (J1)](#4-raspberry-pi-40-pin-gpio-header-j1)
5. [74HC245 Level Shifter (U1)](#5-74hc245-level-shifter-u1)
6. [ADS1015 ADC (U2)](#6-ads1015-adc-u2)
7. [Encoders – Z-Axis (J2) & X-Axis (J3)](#7-encoders--z-axis-j2--x-axis-j3)
8. [ClearPath Servo Signals – Z-Axis (J4) & X-Axis (J5)](#8-clearpath-servo-signals--z-axis-j4--x-axis-j5)
9. [Spindle Index (J6)](#9-spindle-index-j6)
10. [Potentiometer (J7)](#10-potentiometer-j7)
11. [Push Buttons (J8 / J9 / J10)](#11-push-buttons-j8--j9--j10)
12. [Half-Nut Switch (J11)](#12-half-nut-switch-j11)
13. [Limit Switches (J12 / J13 / J14 / J15)](#13-limit-switches-j12--j13--j14--j15)
14. [E-Stop (J16)](#14-e-stop-j16)
15. [Status LEDs](#15-status-leds)
16. [Capacitor Placement Guide](#16-capacitor-placement-guide)
17. [KiCad Libraries & Footprints](#17-kicad-libraries--footprints)
18. [Connector Pinouts & KiCad Footprints](#18-connector-pinouts--kicad-footprints)
19. [Complete BOM with KiCad References](#19-complete-bom-with-kicad-references)
20. [Net Name Convention](#20-net-name-convention)
21. [PCB Layout Tips](#21-pcb-layout-tips)

---

## 1. Power Architecture

### Power Strategy (12V DC jack on HAT + RPi native USB-C)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Power Architecture                               │
│                                                                      │
│  SCENARIO A: 12V Connected (Normal Operation)                       │
│  ─────────────────────────────────────────────                       │
│                                                                      │
│  ┌──────────┐    ┌──────┐    ┌──────────┐    ┌──────────┐          │
│  │ 12V DC   │───→│ Fuse │───→│ MP2307   │───→│ 5V0 Rail │          │
│  │ Jack     │    │  1A  │    │ Buck     │    │          │          │
│  │ (J17)    │    └──────┘    │ 12V→5V   │    │    ┌─────┴─────┐    │
│  └──────────┘                └──────────┘    │    │           │    │
│                                              │    │  ┌────────┴──┐ │
│  ┌──────────┐                ┌──────────┐    │    │  │   RPi    │ │
│  │ (also)   │                │ AP2112   │    │    │  │ GPIO     │ │
│  │ VIN_12V  │───────────────→│ LDO      │───→┼────┤  │ Pin 2→5V │ │
│  └──────────┘                │ 12V→3.3V │    │    │  │ Pin 1→3.3│ │
│                              └──────────┘    │    │  └──────────┘ │
│                                              │    │               │
│                                              │    └──→ HAT logic  │
│                                              │        (5V0 + 3V3) │
│                                              └─────────────────── │
│                                                                      │
│  SCENARIO B: USB-C Only (Bench / Debug, No 12V)                     │
│  ─────────────────────────────────────────────                       │
│                                                                      │
│  ┌──────────────┐                                                    │
│  │ RPi USB-C    │  ← User plugs USB-C into RPi's OWN port           │
│  │ (native)     │  (NOT on HAT — RPi already has it)                │
│  └──────┬───────┘                                                    │
│         │ RPi generates 5V and 3.3V internally                      │
│         │ Back-fed through GPIO header:                             │
│         │  Pin 2 (5V)  ──→ HAT 5V0 rail (via OR-ing diode D12)     │
│         │  Pin 1 (3.3V) ──→ HAT 3V3 rail (via OR-ing diode D15)    │
│         │ HAT regulators are OFF (no 12V input)                     │
│         │ HAT logic runs from RPi back-fed power ✓                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### How It Works

| Scenario | 12V Jack | RPi USB-C | What Happens |
|----------|----------|-----------|-------------|
| **Normal operation** | ✅ Connected | ❌ Not needed | 12V → Buck → 5V rail → RPi Pin 2; 12V → LDO → 3.3V rail → RPi Pin 1 |
| **Bench / debug** | ❌ Not connected | ✅ USB-C to RPi | RPi USB-C → RPi 5V/3.3V → back-fed through GPIO → HAT logic |
| **Both connected** | ✅ Connected | ✅ Also connected | 12V regulators win (higher voltage after diode drop), RPi diodes reverse-biased |

---

## 2. 12 V DC Input & Regulation

### J17 – 12V DC Barrel Jack

**Connector:** 5.5 mm × 2.1 mm DC barrel jack (center-positive)

| Pin | Net Name | Connect To |
|-----|----------|-----------|
| Center (tip) | VIN_12V_RAW | → Fuse F1 (1A slow-blow) → TVS → Buck & LDO inputs |
| Sleeve (outer) | GND | GND plane |

### Input Protection

| Component | Value | Package | KiCad Symbol | KiCad Footprint | Connection |
|-----------|-------|---------|-------------|----------------|-----------|
| F1 | 1 A slow-blow fuse | 1206 | `Fuse` | `Fuse_Holder:Fuse_Holder_1206_Horizontal` | VIN_12V_RAW to VIN_12V |
| D8 | SMAJ13CA (bidirectional TVS) | SMA | `Diode_TVSSMA` | `Diode_SMA` | VIN_12V to GND (transient protection) |
| C7 | 10 µF 25V | 1206 | `C` | `Capacitor_SMD:C_1206` | VIN_12V to GND (input bulk) |
| C8 | 100 nF | 0805 | `C` | `Capacitor_SMD:C_0805` | VIN_12V to GND (input decoupling) |

### U3 – 5V Buck Regulator (12V → 5V)

**Part:** MP2307DN (or LM2596S-5.0 module)
**Package:** SOP-8 (MP2307) or TO-263 (LM2596)
**Output:** 5.0 V fixed, up to 3 A

#### MP2307DN Pinout (SOP-8, top view)

```
        SOP-8
    ┌─────────┐
 VIN │ 1     8 │ GND
 EN  │ 2     7 │ FB (tie to VIN for fixed 5V output, or use resistor divider)
 SW  │ 3     6 │ RT/CT (timer resistor/capacitor)
 GND │ 4     5 │ BOOT
    └─────────┘
```

| Pin | Name | Net Name | Connect To |
|-----|------|----------|-----------|
| 1 | VIN | VIN_12V | 12V rail (after fuse) |
| 2 | EN | 3V3 (or 5V0_EN) | Enable — tie to 3.3V or 5V (always on when powered). Add PNP transistor switch if you want to disable when 12V absent |
| 3 | SW | SW_5V | → Schottky diode (D9) → Output filter → 5V0 |
| 4 | GND | GND | GND plane |
| 5 | BOOT | BOOT_5V | SW → 100nF cap → BOOT |
| 6 | RT/CT | RT_CT | → 22kΩ resistor → GND (sets frequency ~550kHz) |
| 7 | FB | FB_5V | For fixed 5V: tie to output via resistor divider (see below). For MP2307DN (fixed 5V variant): tie FB to GND |
| 8 | GND | GND | GND plane |

#### MP2307 External Components

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| D9 | SS34 Schottky | SMA | `Diode_SMA` | SW (cathode) to 5V0 (anode to SW pin) |
| C9 | 22 µF 16V X5R | 1206 | `Capacitor_SMD:C_1206` | 5V0 to GND (output capacitor) |
| C10 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | 5V0 to GND (output decoupling) |
| C11 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | BOOT to SW (bootstrap cap) |
| R24 | 22 kΩ | 0805 | `Resistor_SMD:R_0805` | RT/CT to GND (frequency set) |
| L1 | 10 µH shielded | 6030 (SMD) | `Inductor_SMD:Inductor_Taiyo_Yuden_GQH101010T` | SW to D9 cathode (inductor between SW and output) |

> **Note:** If using LM2596S-5.0 (fixed 5V module), external components are simpler — just input/output caps and inductor. The module handles feedback internally.

### U4 – 3.3V LDO Regulator (12V → 3.3V)

**Part:** AP2112K-3.3 (ultra-low dropout, 500 mA) or AMS1117-3.3
**Package:** SOT-223 (AP2112) or TO-220 (AMS1117)
**Output:** 3.3 V fixed

#### AP2112K-3.3 Pinout (SOT-223, top view, pins down)

```
    SOT-223 (pad on bottom)
    ┌───┐
    │ 1 │ VIN (12V input)
    │ 2 │ GND
    │ 3 │ GND (thermal pad also GND)
    │ 4 │ VOUT (3.3V output)
    └───┘
```

| Pin | Name | Net Name | Connect To |
|-----|------|----------|-----------|
| 1 | VIN | VIN_12V | 12V rail (after fuse) |
| 2 | GND | GND | GND plane |
| 3 | GND | GND | GND plane + thermal pad |
| 4 | VOUT | 3V3_REG | 3.3V rail (regulated output) |

#### AP2112 External Components

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| C12 | 10 µF 16V | 0805 | `Capacitor_SMD:C_0805` | VIN to GND (input cap) |
| C13 | 10 µF 6.3V X5R | 0805 | `Capacitor_SMD:C_0805` | 3V3_REG to GND (output cap) |
| C14 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | 3V3_REG to GND (output decoupling) |

---

## 3. Power Diode OR-ing (12V Regulators + RPi Back-feed)

### How It Works

The RPi powers itself through its **own native USB-C port** (not on the HAT).
When 12V is present, the HAT regulators power everything. When 12V is absent, the RPi back-feeds power through the GPIO header.

```
  5V Rail OR-ing:

  Buck Output (5V0_BUCK)        RPi GPIO Pin 2 (5V from RPi USB-C)
         │                              │
         │                          ┌───┴───┐
         │                          │  J1   │
         │                          │ Pin 2 │
         │                          │ (GPIO)│
         │                          └───┬───┘
         │                              │
      ┌──┴──┐                       ┌───┴───┐
      │ D11 │                       │  D12  │
      │SS34 │                       │ SS34  │
      │cath │                       │ cath  │
      └──┬──┘                       └───┬───┘
         │  anode ← buck               │  anode ← RPi
         └──────────┬──────────────────┘
                    │
                    ▼
                  5V0 ──────────────────────────────→ HAT 5V logic
                    │
              ┌─────┴─────┐
              │  C5 10µF  │  ← bulk decoupling on 5V0 rail
              └─────┬─────┘
                    │
                   GND


  3.3V Rail OR-ing:

  LDO Output (3V3_REG)          RPi GPIO Pin 1,17 (3.3V from RPi)
         │                              │
         │                          ┌───┴───┐
         │                          │  J1   │
         │                          │Pin 1,17│
         │                          │ (GPIO) │
         │                          └───┬───┘
         │                              │
      ┌──┴──┐                        ┌───┴───┐
      │ D14 │                        │  D15  │
      │SS34 │                        │ SS34  │
      │cath │                        │ cath  │
      └──┬──┘                        └───┬───┘
         │  anode ← LDO                  │  anode ← RPi
         └──────────┬───────────────────┘
                    │
                    ▼
                  3V3 ──────────────────────────────→ HAT 3.3V logic
                    │
              ┌─────┴─────┐
              │  C6 10µF  │  ← bulk decoupling on 3V3 rail
              └─────┬─────┘
                    │
                   GND
```

### Diode OR-ing Components

| Component | Part | Package | KiCad Footprint | Anode | Cathode |
|-----------|------|---------|----------------|-------|---------|
| D11 | SS34 Schottky | SMA | `Diode_SMA` | 5V0_BUCK (buck output) | 5V0 |
| D12 | SS34 Schottky | SMA | `Diode_SMA` | 5V0_RPi (RPi Pin 2) | 5V0 |
| D14 | SS34 Schottky | SMA | `Diode_SMA` | 3V3_REG (LDO output) | 3V3 |
| D15 | SS34 Schottky | SMA | `Diode_SMA` | 3V3_RPi (RPi Pin 1,17) | 3V3 |

### Why Schottky?

- **Low forward drop** (~0.3 V vs ~0.7 V for silicon) — less power wasted as heat
- **Auto-selection** — whichever source has the higher voltage (after diode drop) naturally wins
- **Prevents back-feed** — when 12V is present, buck/LDO outputs win; when no 12V, RPi back-feed wins

### 12V Reverse Protection

When no 12V is connected, the RPi back-feeds 5V/3.3V through the GPIO header. We need to prevent this from back-feeding into the regulator inputs:

| Component | Part | Package | KiCad Footprint | Anode | Cathode |
|-----------|------|---------|----------------|-------|---------|
| D13 | SS34 Schottky | SMA | `Diode_SMA` | VIN_12V (regulator side) | VIN_12V_RAW (jack side) |

This is simple — when no 12V, the diode blocks back-feed. When 12V present, it conducts (~0.3 V drop, still well within buck/LDO input range).

---

## 5. Raspberry Pi 40-Pin GPIO Header (J1)

Standard 2×20 male header. This is the **HAT-to-RPi** interface.

**KiCad Symbol:** `Conn_02x20_Odd_Even` (from `Connector` library)
**KiCad Footprint:** `Pin_Header_Straight_2.54mm:Pin_Header_Male_Straight_2x20_P2.54mm`

| RPi Pin | BCM GPIO | Net Name on HAT | Direction | Connected To |
|---------|----------|-----------------|-----------|--------------|
| 1 | — (3.3V) | 3V3_RPi | Power | → D15 anode → 3V3 OR-ing |
| 2 | — (5V) | 5V0_RPi | Power | → 5V0 net (direct, OR-ing already done before RPi) |
| 3 | GPIO 2 | I2C_SDA | I2C | ADS1015 SDA + 4.7kΩ pull-up to 3V3 |
| 4 | — (5V) | 5V0_RPi | Power | 5V0 rail |
| 5 | GPIO 3 | I2C_SCL | I2C | ADS1015 SCL + 4.7kΩ pull-up to 3V3 |
| 6 | — (GND) | GND | Ground | GND plane |
| 7 | GPIO 4 | HALF_NUT_IN | Input | Half-nut switch via pull-down |
| 8 | GPIO 14 | TXD | (unused) | Pass-through only |
| 9 | — (GND) | GND | Ground | GND plane |
| 10 | GPIO 15 | RXD | (unused) | Pass-through only |
| 11 | GPIO 17 | Z_STEP_3V3 | Output | 74HC245 A1 (3.3V side) |
| 12 | GPIO 18 | — | (unused) | Pass-through only |
| 13 | GPIO 27 | Z_DIR_3V3 | Output | 74HC245 A2 |
| 14 | — (GND) | GND | Ground | GND plane |
| 15 | GPIO 22 | Z_EN_3V3 | Output | 74HC245 A3 |
| 16 | GPIO 23 | X_DIR_3V3 | Output | 74HC245 A5 |
| 17 | — (3.3V) | 3V3_RPi | Power | → D15 anode (same as Pin 1) |
| 18 | GPIO 24 | X_STEP_3V3 | Output | 74HC245 A4 |
| 19 | GPIO 13 | X_ENC_A_IN | Input | X Encoder A (direct, 3.3V) |
| 20 | — (GND) | GND | Ground | GND plane |
| 21 | GPIO 26 | BTN1_IN | Input | Button 1 via pull-up |
| 22 | GPIO 25 | X_EN_3V3 | Output | 74HC245 A6 |
| 23 | GPIO 11 | LIM_X_MINUS_IN | Input | Limit X− via pull-up |
| 24 | GPIO 8 | LIM_X_PLUS_IN | Input | Limit X+ via pull-up |
| 25 | — (GND) | GND | Ground | GND plane |
| 26 | GPIO 7 | LIM_Z_MINUS_IN | Input | Limit Z− via pull-up |
| 27 | GPIO 0 | — | (unused) | Pass-through only |
| 28 | GPIO 1 | — | (unused) | Pass-through only |
| 29 | GPIO 5 | Z_ENC_A_IN | Input | Z Encoder A (direct, 3.3V) |
| 30 | — (GND) | GND | Ground | GND plane |
| 31 | GPIO 6 | Z_ENC_B_IN | Input | Z Encoder B (direct, 3.3V) |
| 32 | GPIO 12 | SPINDLE_IN | Input | Spindle index via voltage divider |
| 33 | GPIO 13 | X_ENC_A_IN | Input | X Encoder A (same net as Pin 19) |
| 34 | — (GND) | GND | Ground | GND plane |
| 35 | GPIO 19 | X_ENC_B_IN | Input | X Encoder B (direct, 3.3V) |
| 36 | GPIO 16 | LIM_Z_PLUS_IN | Input | Limit Z+ via pull-up |
| 37 | GPIO 26 | BTN1_IN | Input | Button 1 (same net as Pin 21) |
| 38 | GPIO 20 | BTN2_IN | Input | Button 2 via pull-up |
| 39 | — (GND) | GND | Ground | GND plane |
| 40 | GPIO 21 | BTN3_IN | Input | Button 3 via pull-up |

---

## 6. 74HC245 Level Shifter (U1)

**Part:** 74HC245PW (TSSOP-20) or 74HC245D (SOIC-20)
**Function:** Octal bus transceiver, directional A→B (unidirectional for our use)
**Supply:** Single 5V supply — reads 3.3V inputs on A side as HIGH, outputs full 5V on B side

### Why 74HC245 Works for 3.3V → 5V

- **VCC = 5V:** HI-input threshold ≈ 3.5V (typical). 3.3V from RPi is close but **generally works** in practice (HC family V_IH_min = 0.6 × VCC = 3.0V at 5V supply, so 3.3V > 3.0V ✓)
- **Output at 5V:** Full 5V TTL-level output on B side → ClearPath servo inputs happy
- **Direction:** Fixed A→B (DIR pin tied HIGH)

### 74HC245 Pinout (TSSOP-20 / SOIC-20)

```
            TSSOP-20 / SOIC-20
        ┌─────────────────┐
  A1    │ 1             20 │ VCC (5V)
  A2    │ 2             19 │ B8
  A3    │ 3             18 │ B7
  A4    │ 4             17 │ B6
  A5    │ 5             16 │ B5
  A6    │ 6             15 │ B4
  A7    │ 7             14 │ B3
  A8    │ 8             13 │ B2
  GND   │ 9             12 │ B1
  /CE   │10             11 │ DIR
        └─────────────────┘
```

### Power & Control Pins

| Pin | Name | Net Name | Connect To | Why |
|-----|------|----------|-----------|-----|
| 20 | VCC | 5V0 | 5V rail | Single 5V supply |
| 9 | GND | GND | GND plane | |
| 11 | DIR | 5V0 | Tie to 5V (HIGH) | Fixed direction A→B |
| 10 | /CE (OE̅) | GND | Tie to GND (LOW) | Chip always enabled |

### Channel Assignments (A→B, unidirectional)

| Pin A | Name A | Net Name (A side, 3.3V) | From GPIO | Pin B | Name B | Net Name (B side, 5V) | To Connector |
|-------|--------|-------------------------|-----------|-------|--------|----------------------|--------------|
| 1 | A1 | Z_STEP_3V3 | GPIO 17 | 12 | B1 | Z_STEP_5V | → 100Ω → J4 (Z Motor STEP) |
| 2 | A2 | Z_DIR_3V3 | GPIO 27 | 13 | B2 | Z_DIR_5V | → 100Ω → J4 (Z Motor DIR) |
| 3 | A3 | Z_EN_3V3 | GPIO 22 | 14 | B3 | Z_EN_5V | → J4 (Z Motor ENABLE) |
| 4 | A4 | X_STEP_3V3 | GPIO 24 | 15 | B4 | X_STEP_5V | → 100Ω → J5 (X Motor STEP) |
| 5 | A5 | X_DIR_3V3 | GPIO 23 | 16 | B5 | X_DIR_5V | → 100Ω → J5 (X Motor DIR) |
| 6 | A6 | X_EN_3V3 | GPIO 25 | 17 | B6 | X_EN_5V | → J5 (X Motor ENABLE) |
| 7 | A7 | (spare) | — | 18 | B7 | (spare) | — |
| 8 | A8 | (spare) | — | 19 | B8 | (spare) | — |

### Decoupling

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| C1 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | Pin 20 (VCC) to GND — place as close to pin as possible |

---

## 7. ADS1015 ADC (U2)

**Part:** ADS1015IDGSR
**Package:** VSSOP-10 (tiny!) or use a breakout module
**Function:** 4-channel 12-bit ADC, I2C interface
**I2C Address:** 0x48 (default, A0 floating or GND)

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `ADS1015` (from `Analog_Converter_ADC` library) |
| **Footprint** | `Package_DFN_QFN:VSSOP-10_3x3mm_P0.65mm` |

> **Tip:** VSSOP-10 is very small (3×3 mm, 0.65 mm pitch). If hand-soldering, consider using an ADS1015 breakout module (through-hole) or the ADS1115 in SOIC-16 (larger, easier to solder).

### Pinout (VSSOP-10)

```
        VSSOP-10 (3x3 mm)
    ┌────────────┐
 SDA │ 1      10 │ AVSS
 SCL │ 2      9 │ AVDD
 A0  │ 3      8 │ AIN1
 GND │ 4      7 │ AIN0
 DVDD│ 5      6 │ DVSS
    └────────────┘
```

### Connections

| Pin | Name | Net Name | Connect To |
|-----|------|----------|-----------|
| 1 | SDA | I2C_SDA | RPi GPIO 2 (Pin 3) + 4.7kΩ pull-up to 3V3 |
| 2 | SCL | I2C_SCL | RPi GPIO 3 (Pin 5) + 4.7kΩ pull-up to 3V3 |
| 3 | A0 | GND | GND (I2C address 0x48) |
| 4 | GND | GND | GND plane |
| 5 | DVDD | 3V3 | 3.3V rail |
| 6 | DVSS | GND | GND plane |
| 7 | AIN0 | POT_WIPER_ADC | Potentiometer wiper via 10kΩ series resistor |
| 8 | AIN1 | (unconnected) | — |
| 9 | AVDD | 3V3 | 3.3V rail |
| 10 | AVSS | GND | GND plane |

### Decoupling (critical for ADC accuracy)

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| C2 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | AVDD (Pin 9) to AVSS (Pin 10) — place directly across pins |
| C3 | 100 nF | 0805 | `Capacitor_SMD:C_0805` | DVDD (Pin 5) to DVSS (Pin 6) — place directly across pins |
| C4 | 10 µF | 0805 | `Capacitor_SMD:C_0805` | 3V3 to GND (near ADS1015, bulk decoupling) |

---

## 8. Encoders – Z-Axis (J2) & X-Axis (J3)

**Connector:** 6-pin JST PH 2.0 mm pitch (per axis)
**Encoder:** CUI AMT103-V (2000 CPR, quadrature, 3.3V compatible)

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `JST_PH_6pin` (from `Connector_JST` library) or `Conn_01x06` (generic) |
| **Footprint** | `Connector_JST:JST_PH_6Pin_2.00mm_Pitch` |

### J2 – Z-Axis Encoder

| J2 Pin | JST Wire | Net Name | Connect To |
|--------|----------|----------|-----------|
| 1 | VCC | 3V3 | 3.3V rail |
| 2 | GND | GND | GND plane |
| 3 | A | Z_ENC_A_IN | RPi GPIO 5 (Pin 29) |
| 4 | B | Z_ENC_B_IN | RPi GPIO 6 (Pin 31) |
| 5 | INDEX | (unconnected) | — |
| 6 | NC | (unconnected) | — |

### J3 – X-Axis Encoder

| J3 Pin | JST Wire | Net Name | Connect To |
|--------|----------|----------|-----------|
| 1 | VCC | 3V3 | 3.3V rail |
| 2 | GND | GND | GND plane |
| 3 | A | X_ENC_A_IN | RPi GPIO 13 (Pin 33) |
| 4 | B | X_ENC_B_IN | RPi GPIO 19 (Pin 35) |
| 5 | INDEX | (unconnected) | — |
| 6 | NC | (unconnected) | — |

### Encoder Pull-ups (optional — DNP if AMT103-V uses internal pull-ups)

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R1 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | Z_ENC_A_IN to 3V3 |
| R2 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | Z_ENC_B_IN to 3V3 |
| R3 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | X_ENC_A_IN to 3V3 |
| R4 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | X_ENC_B_IN to 3V3 |

---

## 9. ClearPath Servo Signals – Z-Axis (J4) & X-Axis (J5)

**Connector:** 8-pin Molex Mini-fit Jr. (or 2.54 mm pitch header)

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Conn_01x08` (from `Connector` library) |
| **Footprint** | `Connector_Molex:Molex_KK-254_1x08_P2.54mm_Horizontal` (for KK-254 style) or `Pin_Header_Straight_2.54mm:Pin_Header_Male_Straight_1x08_P2.54mm` |

### J4 – Z-Axis Servo Signal

| J4 Pin | Net Name | Signal Source | Notes |
|--------|----------|--------------|-------|
| 1 | Z_STEP_5V | 74HC245 B1 → 100Ω series | 5V TTL STEP |
| 2 | Z_DIR_5V | 74HC245 B2 → 100Ω series | 5V TTL DIR |
| 3 | Z_EN_5V | 74HC245 B3 (direct) | 5V TTL ENABLE |
| 4 | HLFB_Z | (unconnected) | Hardware feedback — not used |
| 5 | GND | GND | Signal ground |
| 6 | 5V0 | 5V0 | Logic power for ClearPath |
| 7 | (HV+) | (unconnected) | 70V supplied externally |
| 8 | (HV−) | (unconnected) | 70V supplied externally |

### J5 – X-Axis Servo Signal

| J5 Pin | Net Name | Signal Source | Notes |
|--------|----------|--------------|-------|
| 1 | X_STEP_5V | 74HC245 B4 → 100Ω series | 5V TTL STEP |
| 2 | X_DIR_5V | 74HC245 B5 → 100Ω series | 5V TTL DIR |
| 3 | X_EN_5V | 74HC245 B6 (direct) | 5V TTL ENABLE |
| 4 | HLFB_X | (unconnected) | Hardware feedback — not used |
| 5 | GND | GND | Signal ground |
| 6 | 5V0 | 5V0 | Logic power for ClearPath |
| 7 | (HV+) | (unconnected) | 70V supplied externally |
| 8 | (HV−) | (unconnected) | 70V supplied externally |

### Series Resistors (signal integrity on STEP lines)

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R5 | 100 Ω | 0805 | `Resistor_SMD:R_0805` | 74HC245 B1 to J4 Pin 1 |
| R6 | 100 Ω | 0805 | `Resistor_SMD:R_0805` | 74HC245 B4 to J5 Pin 1 |

### ESD Protection

| Component | Part | Package | KiCad Symbol | KiCad Footprint | Connection |
|-----------|------|---------|-------------|----------------|-----------|
| D1–D6 | PESD5V0S1UL | SOD-323 | `Diode_TVSSOD323` | `Diode_SOD-323` | One per motor signal (STEP/DIR/ENABLE × 2), signal to GND |

---

## 10. Spindle Index (J6)

**Connector:** 3-pin JST PH 2.0 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Conn_01x03` (from `Connector` library) |
| **Footprint** | `Connector_JST:JST_PH_3Pin_2.00mm_Pitch` |

### J6 – Spindle Index Connector

| J6 Pin | Net Name | External Wire |
|--------|----------|--------------|
| 1 | 5V0 | To AutoTech C3 +5V |
| 2 | GND | Common ground |
| 3 | SPINDLE_RAW | Raw 5V TTL from C3 |

### Voltage Divider (5V → 3.3V)

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R7 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | SPINDLE_RAW to SPINDLE_IN (top) |
| R8 | 20 kΩ | 0805 | `Resistor_SMD:R_0805` | SPINDLE_IN to GND (bottom) |

**Output:** SPINDLE_IN ≈ 3.33V at HIGH → RPi GPIO 12 (Pin 32)

### ESD Protection

| Component | Part | Package | KiCad Footprint | Connection |
|-----------|------|---------|----------------|-----------|
| D7 | PESD5V0S1UL | SOD-323 | `Diode_SOD-323` | SPINDLE_RAW to GND |

---

## 11. Potentiometer (J7)

**Connector:** 3-pin JST PH 2.0 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Conn_01x03` |
| **Footprint** | `Connector_JST:JST_PH_3Pin_2.00mm_Pitch` |

### J7 – Potentiometer Connector

| J7 Pin | Net Name | External Wire |
|--------|----------|--------------|
| 1 | 5V0 | Pot end A (5V) |
| 2 | POT_WIPER | Pot wiper → 10kΩ → ADS1015 AIN0 |
| 3 | GND | Pot end B |

### Series Resistor (ADC input protection)

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R9 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | POT_WIPER to POT_WIPER_ADC (ADS1015 AIN0) |

---

## 12. Push Buttons (J8 / J9 / J10)

**Connector:** 2-pin screw terminal, 3.5 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Screw_Terminal_02pin` (from `Connector` library) |
| **Footprint** | `Connector_Screw_Terminal_3.50mm:Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` |

### Connections

| Connector | Pin | Net Name | Connect To |
|-----------|-----|----------|-----------|
| J8 (BTN1) | 1 | BTN1_IN | RPi GPIO 26 + 10kΩ pull-up to 3V3 |
| J8 (BTN1) | 2 | GND | GND |
| J9 (BTN2) | 1 | BTN2_IN | RPi GPIO 20 + 10kΩ pull-up to 3V3 |
| J9 (BTN2) | 2 | GND | GND |
| J10 (BTN3) | 1 | BTN3_IN | RPi GPIO 21 + 10kΩ pull-up to 3V3 |
| J10 (BTN3) | 2 | GND | GND |

### Button Pull-up Resistors

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R10 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | BTN1_IN to 3V3 |
| R11 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | BTN2_IN to 3V3 |
| R12 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | BTN3_IN to 3V3 |

---

## 13. Half-Nut Switch (J11)

**Connector:** 2-pin screw terminal, 3.5 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Screw_Terminal_02pin` |
| **Footprint** | `Connector_Screw_Terminal_3.50mm:Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` |

| J11 Pin | Net Name | Connect To |
|---------|----------|-----------|
| 1 | HALF_NUT_IN | RPi GPIO 4 + 10kΩ pull-down to GND |
| 2 | GND | GND |

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R13 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | HALF_NUT_IN to GND (pull-down) |

---

## 14. Limit Switches (J12 / J13 / J14 / J15)

**Connector:** 2-pin screw terminal, 3.5 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Screw_Terminal_02pin` |
| **Footprint** | `Connector_Screw_Terminal_3.50mm:Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` |

### Connections

| Connector | Pin | Net Name | Connect To |
|-----------|-----|----------|-----------|
| J12 (LIM Z+) | 1 | LIM_Z_PLUS_IN | RPi GPIO 16 + 10kΩ pull-up to 3V3 |
| J12 (LIM Z+) | 2 | GND | GND |
| J13 (LIM Z−) | 1 | LIM_Z_MINUS_IN | RPi GPIO 7 + 10kΩ pull-up to 3V3 |
| J13 (LIM Z−) | 2 | GND | GND |
| J14 (LIM X+) | 1 | LIM_X_PLUS_IN | RPi GPIO 8 + 10kΩ pull-up to 3V3 |
| J14 (LIM X+) | 2 | GND | GND |
| J15 (LIM X−) | 1 | LIM_X_MINUS_IN | RPi GPIO 11 + 10kΩ pull-up to 3V3 |
| J15 (LIM X−) | 2 | GND | GND |

### Limit Switch Pull-up Resistors

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R14 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | LIM_Z_PLUS_IN to 3V3 |
| R15 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | LIM_Z_MINUS_IN to 3V3 |
| R16 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | LIM_X_PLUS_IN to 3V3 |
| R17 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | LIM_X_MINUS_IN to 3V3 |

---

## 15. E-Stop (J16)

**Connector:** 4-pin screw terminal, 3.5 mm pitch

### KiCad References

| Item | Value |
|------|-------|
| **Symbol** | `Screw_Terminal_04pin` (from `Connector` library) |
| **Footprint** | `Connector_Screw_Terminal_3.50mm:Screw_Terminal_Kyocera_3503_04pin_3.50mm_Horizontal` |

| J16 Pin | Net Name | Connect To | Notes |
|---------|----------|-----------|-------|
| 1 | ESTOP_NC | Hard-wired to ENABLE lines | NC contact — breaks servo ENABLE (HARD safety) |
| 2 | ESTOP_IN | RPi GPIO (free pin) + 10kΩ pull-up to 3V3 | NO contact — software detection |
| 3 | ESTOP_COM | Common terminal | |
| 4 | GND | GND | |

| Component | Value | Package | KiCad Footprint | Connection |
|-----------|-------|---------|----------------|-----------|
| R18 | 10 kΩ | 0805 | `Resistor_SMD:R_0805` | ESTOP_IN to 3V3 (pull-up) |

---

## 16. Status LEDs

### LED1 – Power (Green) — 12V present

| Component | Value | Package | KiCad Symbol | KiCad Footprint | Connection |
|-----------|-------|---------|-------------|----------------|-----------|
| LED1 | Green | 0805 | `LED` | `LED_SMD:LED_0805` | Anode via R19 to VIN_12V, Cathode to GND |
| R19 | 1 kΩ | 0805 | `R` | `Resistor_SMD:R_0805` | VIN_12V to LED1 anode (1kΩ for 12V: (12-2)/1000 ≈ 10 mA) |

### LED2 – E-Stop Triggered (Red)

| Component | Value | Package | KiCad Symbol | KiCad Footprint | Connection |
|-----------|-------|---------|-------------|----------------|-----------|
| LED2 | Red | 0805 | `LED` | `LED_SMD:LED_0805` | Anode via R20 to ESTOP_IN, Cathode to GND |
| R20 | 330 Ω | 0805 | `R` | `Resistor_SMD:R_0805` | ESTOP_IN to LED2 anode |

### LED3 – Activity / Step Pulse (Yellow)

| Component | Value | Package | KiCad Symbol | KiCad Footprint | Connection |
|-----------|-------|---------|-------------|----------------|-----------|
| LED3 | Yellow | 0805 | `LED` | `LED_SMD:LED_0805` | Anode via R21 to Z_STEP_5V, Cathode to GND |
| R21 | 330 Ω | 0805 | `R` | `Resistor_SMD:R_0805` | Z_STEP_5V to LED3 anode |

---

## 17. Capacitor Placement Guide

### Decoupling Capacitors (per IC — place as close to power pins as possible)

| Cap | Value | Location | Why |
|-----|-------|----------|-----|
| C1 | 100 nF | 74HC245 Pin 20 (VCC) to GND | Digital IC decoupling — keep within 2 mm of pin |
| C2 | 100 nF | ADS1015 Pin 9 (AVDD) to Pin 10 (AVSS) | Analog supply — critical for ADC accuracy |
| C3 | 100 nF | ADS1015 Pin 5 (DVDD) to Pin 6 (DVSS) | Digital supply |
| C4 | 10 µF | Near ADS1015, 3V3 to GND | Bulk decoupling for ADC |

### Power Rail Capacitors

| Cap | Value | Location | Why |
|-----|-------|----------|-----|
| C5 | 10 µF | 5V0 rail, near 74HC245 | Bulk decoupling on 5V rail |
| C6 | 10 µF | 3V3 rail, near GPIO header | Bulk decoupling on 3.3V rail |
| C7 | 10 µF 25V | VIN_12V, near DC jack | Input bulk capacitance |
| C8 | 100 nF | VIN_12V, near C7 | Input high-frequency decoupling |
| C9 | 22 µF 16V | 5V0 buck output | Buck regulator output capacitor |
| C10 | 100 nF | 5V0 buck output, near C9 | Buck output decoupling |
| C11 | 100 nF | 74HC245 BOOT to SW | Bootstrap capacitor for buck |
| C12 | 10 µF 16V | AP2112 VIN | LDO input capacitor |
| C13 | 10 µF 6.3V | AP2112 VOUT (3V3_REG) | LDO output capacitor (required for stability) |
| C14 | 100 nF | 3V3_REG, near C13 | LDO output decoupling |

### I2C Bus Capacitors

| Cap | Value | Location | Why |
|-----|-------|----------|-----|
| (none recommended) | — | I2C lines | **Do NOT add caps on I2C SDA/SCL** — the 4.7kΩ pull-ups are sufficient. Extra capacitance slows rise time and can cause I2C errors at 400 kHz. Keep I2C traces short (< 5 cm) instead. |

> **I2C Best Practice:** The ADS1015 adds ~5 pF input capacitance per line. With short traces (< 5 cm, ~100 pF trace capacitance), total bus capacitance is well within the 400 pF I2C spec limit. **No additional capacitors needed on I2C.**

### General Rules

1. **Every IC power pin** gets a 100 nF ceramic cap within 2 mm (preferably on the same layer, no via)
2. **Each power rail** gets at least one 10 µF bulk cap near the load cluster
3. **Regulator inputs/outputs** get the capacitors specified in the datasheet (non-negotiable for stability)
4. **Keep GND plane solid** — no splits, use it as the return path for all decoupling caps
5. **Place decoupling before vias** — cap should be between the IC pin and any via to the GND plane

---

## 18. KiCad Libraries & Footprints

### Libraries to Install / Enable in KiCad

These are all in the **KiCad 6/7/8 default symbol/footprint libraries**:

| Library Name | Contents | Enable In |
|-------------|----------|-----------|
| `Device` | Resistors, capacitors, diodes, LEDs, fuses | Symbol library |
| `Connector` | GPIO headers, screw terminals, generic connectors | Symbol + Footprint |
| `Connector_JST` | JST PH connectors (2.00 mm pitch) | Symbol + Footprint |
| `Connector_Molex` | Molex KK-254, Mini-fit Jr. | Footprint library |
| `Connector_Screw_Terminal_3.50mm` | 3.5 mm pitch screw terminals | Footprint library |
| `Analog_Converter_ADC` | ADS1015, ADS1115 | Symbol library |
| `74HC` | 74HC245, 74HCxx series | Symbol library |
| `Regulator_Switching` | MP2307, LM2596, buck converters | Symbol library |
| `Regulator_LDO` | AP2112, AMS1117, LDO regulators | Symbol library |
| `Diode` | Schottky diodes, TVS diodes | Symbol library |
| `Package_TO_SOT_SMD` | SOT-223, SOT-23 packages | Footprint library |
| `Package_SON` | VSSOP packages | Footprint library |
| `Package_SO` | SOIC, TSSOP packages | Footprint library |
| `Package_DFN_QFN` | VSSOP-10 (for ADS1015) | Footprint library |
| `Capacitor_SMD` | C_0402, C_0603, C_0805, C_1206 | Footprint library |
| `Resistor_SMD` | R_0402, R_0603, R_0805, R_1206 | Footprint library |
| `LED_SMD` | LED_0603, LED_0805 | Footprint library |
| `Inductor_SMD` | Shielded power inductors | Footprint library |
| `Fuse_Holder` | SMD fuse holders | Footprint library |

### Components to Import (Symbol → Footprint Mapping)

| Component | Symbol Library | Symbol Name | Footprint Library | Footprint Name |
|-----------|--------------|-------------|------------------|---------------|
| 74HC245 | `74HC` | `74HC245` | `Package_SO` | `TSSOP-20_4.4x6.5mm_P0.65mm` |
| ADS1015 | `Analog_Converter_ADC` | `ADS1015` | `Package_DFN_QFN` | `VSSOP-10_3x3mm_P0.65mm` |
| MP2307 | `Regulator_Switching` | `MP2307` | `Package_SO` | `SOP-8_3.9x4.9mm_P1.27mm` |
| AP2112-3.3 | `Regulator_LDO` | `AP2112K-3.3` | `Package_TO_SOT_SMD` | `SOT-223-3_TabPin2` |
| SS34 Schottky | `Diode` | `SS34` | `Diode_SMA` | `Diode_SMA` |
| PESD5V0S1UL TVS | `Diode` | `PESD5V0S1UL` | `Diode_SOD-323` | `Diode_SOD-323` |
| SMAJ13CA TVS | `Diode` | `SMAJ13CA` | `Diode_SMA` | `Diode_SMA` |
| DC Jack 5.5×2.1 | `Connector` | `Jack_1` | `Connector` | `Jack_5.5mm_PadJustAGND` |
| RPi GPIO 2×20 | `Connector` | `Conn_02x20_Odd_Even` | `Pin_Header_Straight_2.54mm` | `Pin_Header_Male_Straight_2x20_P2.54mm` |
| JST PH 6-pin | `Connector_JST` | `JST_PH_6pin` | `Connector_JST` | `JST_PH_6Pin_2.00mm_Pitch` |
| JST PH 3-pin | `Connector_JST` | `JST_PH_3pin` | `Connector_JST` | `JST_PH_3Pin_2.00mm_Pitch` |
| Screw Terminal 2-pin | `Connector` | `Screw_Terminal_02pin` | `Connector_Screw_Terminal_3.50mm` | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` |
| Screw Terminal 4-pin | `Connector` | `Screw_Terminal_04pin` | `Connector_Screw_Terminal_3.50mm` | `Screw_Terminal_Kyocera_3503_04pin_3.50mm_Horizontal` |
| Molex KK-254 8-pin | `Connector` | `Conn_01x08` | `Connector_Molex` | `Molex_KK-254_1x08_P2.54mm_Horizontal` |
| 1A Fuse 1206 | `Device` | `Fuse` | `Fuse_Holder` | `Fuse_Holder_1206_Horizontal` |
| 10 µH Inductor | `Device` | `L` | `Inductor_SMD` | `Inductor_Taiyo_Yuden_GQH101010T` |
| Resistor | `Device` | `R` | `Resistor_SMD` | `R_0805` |
| Capacitor | `Device` | `C` | `Capacitor_SMD` | `C_0805` (or `C_1206` for larger values) |
| LED | `Device` | `LED` | `LED_SMD` | `LED_0805` |

---

## 19. Connector Pinouts & KiCad Footprints

### Summary of All Connectors

| Designator | Type | Pins | KiCad Footprint | Location on PCB |
|-----------|------|------|----------------|----------------|
| J1 | RPi GPIO 2×20 | 40 | `Pin_Header_Male_Straight_2x20_P2.54mm` | Center (stacks onto RPi) |
| J2 | JST PH 6-pin (Z Encoder) | 6 | `JST_PH_6Pin_2.00mm_Pitch` | Edge (cable exit) |
| J3 | JST PH 6-pin (X Encoder) | 6 | `JST_PH_6Pin_2.00mm_Pitch` | Edge (cable exit) |
| J4 | Molex 8-pin (Z Servo) | 8 | `Molex_KK-254_1x08_P2.54mm_Horizontal` | Edge (cable exit) |
| J5 | Molex 8-pin (X Servo) | 8 | `Molex_KK-254_1x08_P2.54mm_Horizontal` | Edge (cable exit) |
| J6 | JST PH 3-pin (Spindle) | 3 | `JST_PH_3Pin_2.00mm_Pitch` | Edge (cable exit) |
| J7 | JST PH 3-pin (Pot) | 3 | `JST_PH_3Pin_2.00mm_Pitch` | Edge (cable exit) |
| J8 | Screw Terminal 2-pin (BTN1) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J9 | Screw Terminal 2-pin (BTN2) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J10 | Screw Terminal 2-pin (BTN3) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J11 | Screw Terminal 2-pin (Half-Nut) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J12 | Screw Terminal 2-pin (LIM Z+) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J13 | Screw Terminal 2-pin (LIM Z−) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J14 | Screw Terminal 2-pin (LIM X+) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J15 | Screw Terminal 2-pin (LIM X−) | 2 | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` | Edge |
| J16 | Screw Terminal 4-pin (E-Stop) | 4 | `Screw_Terminal_Kyocera_3503_04pin_3.50mm_Horizontal` | Edge |
| J17 | DC Barrel Jack 5.5×2.1 | 2 | `Jack_5.5mm_PadJustAGND` | Edge (power input) |

---

## 20. Complete BOM with KiCad References

### ICs

| Qty | Designator | Part | Package | KiCad Symbol | KiCad Footprint |
|-----|-----------|------|---------|-------------|----------------|
| 1 | U1 | 74HC245PW | TSSOP-20 | `74HC:74HC245` | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` |
| 1 | U2 | ADS1015IDGSR | VSSOP-10 | `Analog_Converter_ADC:ADS1015` | `Package_DFN_QFN:VSSOP-10_3x3mm_P0.65mm` |
| 1 | U3 | MP2307DN (5V fixed) | SOP-8 | `Regulator_Switching:MP2307` | `Package_SO:SOP-8_3.9x4.9mm_P1.27mm` |
| 1 | U4 | AP2112K-3.3 | SOT-223 | `Regulator_LDO:AP2112K-3.3` | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` |

### Diodes

| Qty | Designator | Part | Package | KiCad Symbol | KiCad Footprint |
|-----|-----------|------|---------|-------------|----------------|
| 1 | D8 | SMAJ13CA (TVS) | SMA | `Diode:SMAJ13CA` | `Diode_SMA:Diode_SMA` |
| 1 | D9 | SS34 (Schottky, buck) | SMA | `Diode:SS34` | `Diode_SMA:Diode_SMA` |
| 2 | D11, D12 | SS34 (5V OR-ing) | SMA | `Diode:SS34` | `Diode_SMA:Diode_SMA` |
| 2 | D14, D15 | SS34 (3.3V OR-ing) | SMA | `Diode:SS34` | `Diode_SMA:Diode_SMA` |
| 1 | D13 | SS34 (12V reverse protection) | SMA | `Diode:SS34` | `Diode_SMA:Diode_SMA` |
| 6 | D1–D6 | PESD5V0S1UL (TVS) | SOD-323 | `Diode:PESD5V0S1UL` | `Diode_SOD-323:Diode_SOD-323` |
| 1 | D7 | PESD5V0S1UL (TVS, spindle) | SOD-323 | `Diode:PESD5V0S1UL` | `Diode_SOD-323:Diode_SOD-323` |

**Total Schottky diodes: 7 (SS34)**
**Total TVS diodes: 8 (1× SMAJ13CA + 7× PESD5V0S1UL)**

### Resistors (all 0805 unless noted)

| Qty | Designator | Value | Function |
|-----|-----------|-------|----------|
| 4 | R1–R4 | 10 kΩ | Encoder pull-ups (optional, DNP) |
| 2 | R5–R6 | 100 Ω | STEP line series |
| 1 | R7 | 10 kΩ | Spindle divider top |
| 1 | R8 | 20 kΩ | Spindle divider bottom |
| 1 | R9 | 10 kΩ | Potentiometer series |
| 3 | R10–R12 | 10 kΩ | Button pull-ups |
| 1 | R13 | 10 kΩ | Half-nut pull-down |
| 4 | R14–R17 | 10 kΩ | Limit switch pull-ups |
| 1 | R18 | 10 kΩ | E-Stop pull-up |
| 1 | R19 | 1 kΩ | LED1 current limit (12V) |
| 1 | R20 | 330 Ω | LED2 current limit |
| 1 | R21 | 330 Ω | LED3 current limit |
| 2 | R22–R23 | 4.7 kΩ | I2C pull-ups (SDA/SCL) |
| 1 | R24 | 22 kΩ | MP2307 frequency set |
**Total resistors: 24**

### Capacitors

| Qty | Designator | Value | Voltage | Package | Function |
|-----|-----------|-------|---------|---------|----------|
| 1 | C1 | 100 nF | 10V | 0805 | 74HC245 decoupling |
| 2 | C2–C3 | 100 nF | 10V | 0805 | ADS1015 AVDD/DVDD decoupling |
| 1 | C4 | 10 µF | 6.3V | 0805 | ADS1015 bulk |
| 1 | C5 | 10 µF | 10V | 0805 | 5V0 bulk |
| 1 | C6 | 10 µF | 6.3V | 0805 | 3V3 bulk |
| 1 | C7 | 10 µF | 25V | 1206 | 12V input bulk |
| 1 | C8 | 100 nF | 25V | 0805 | 12V input decoupling |
| 1 | C9 | 22 µF | 16V | 1206 | Buck output |
| 1 | C10 | 100 nF | 16V | 0805 | Buck output decoupling |
| 1 | C11 | 100 nF | 16V | 0805 | Buck bootstrap |
| 1 | C12 | 10 µF | 16V | 0805 | LDO input |
| 1 | C13 | 10 µF | 6.3V | 0805 | LDO output |
| 1 | C14 | 100 nF | 10V | 0805 | 3V3_REG decoupling |

**Total capacitors: 14**

### Inductors

| Qty | Designator | Value | Package | KiCad Footprint |
|-----|-----------|-------|---------|----------------|
| 1 | L1 | 10 µH shielded | 6030 (SMD) | `Inductor_SMD:Inductor_Taiyo_Yuden_GQH101010T` |

### LEDs

| Qty | Designator | Color | Package | KiCad Footprint |
|-----|-----------|-------|---------|----------------|
| 1 | LED1 | Green | 0805 | `LED_SMD:LED_0805` |
| 1 | LED2 | Red | 0805 | `LED_SMD:LED_0805` |
| 1 | LED3 | Yellow | 0805 | `LED_SMD:LED_0805` |

### Connectors

| Qty | Designator | Type | KiCad Footprint |
|-----|-----------|------|----------------|
| 1 | J1 | RPi GPIO 2×20 male | `Pin_Header_Male_Straight_2x20_P2.54mm` |
| 2 | J2, J3 | JST PH 6-pin | `JST_PH_6Pin_2.00mm_Pitch` |
| 2 | J4, J5 | Molex KK-254 8-pin | `Molex_KK-254_1x08_P2.54mm_Horizontal` |
| 2 | J6, J7 | JST PH 3-pin | `JST_PH_3Pin_2.00mm_Pitch` |
| 9 | J8–J16 | Screw terminal 2-pin | `Screw_Terminal_Kyocera_3503_02pin_3.50mm_Horizontal` |
| 1 | J16 | Screw terminal 4-pin | `Screw_Terminal_Kyocera_3503_04pin_3.50mm_Horizontal` |
| 1 | J17 | DC barrel jack 5.5×2.1 | `Jack_5.5mm_PadJustAGND` |

### Protection

| Qty | Designator | Part | Package | KiCad Footprint |
|-----|-----------|------|---------|----------------|
| 1 | F1 | 1 A slow-blow fuse | 1206 | `Fuse_Holder_1206_Horizontal` |

---

## 21. Net Name Convention

| Prefix | Meaning | Examples |
|--------|---------|----------|
| `VIN_12V_RAW` | Raw 12V from DC jack (before fuse) | VIN_12V_RAW |
| `VIN_12V` | 12V rail (after fuse & protection) | VIN_12V |
| `5V0_BUCK` | Buck regulator output (before OR-ing) | 5V0_BUCK |
| `5V0` | OR'd 5V rail (final, feeds RPi + HAT) | 5V0 |
| `5V0_RPi` | 5V net at RPi GPIO header pins | 5V0_RPi |
| `3V3_REG` | LDO regulator output (before OR-ing) | 3V3_REG |
| `3V3_RPi` | 3.3V net at RPi GPIO header pins | 3V3_RPi |
| `3V3` | OR'd 3.3V rail (final, feeds HAT logic) | 3V3 |
| `GND` | Common ground | GND |
| `Z_STEP_3V3` | Z STEP on 3.3V side of 74HC245 | Z_STEP_3V3, Z_DIR_3V3, Z_EN_3V3 |
| `Z_STEP_5V` | Z STEP on 5V side of 74HC245 | Z_STEP_5V, Z_DIR_5V, Z_EN_5V |
| `X_STEP_3V3` | X STEP on 3.3V side of 74HC245 | X_STEP_3V3, X_DIR_3V3, X_EN_3V3 |
| `X_STEP_5V` | X STEP on 5V side of 74HC245 | X_STEP_5V, X_DIR_5V, X_EN_5V |
| `Z_ENC_A_IN` | Z encoder A | Z_ENC_A_IN, Z_ENC_B_IN |
| `X_ENC_A_IN` | X encoder A | X_ENC_A_IN, X_ENC_B_IN |
| `SPINDLE_RAW` | Raw 5V spindle signal | SPINDLE_RAW |
| `SPINDLE_IN` | Conditioned 3.3V spindle | SPINDLE_IN |
| `POT_WIPER` | Potentiometer wiper (connector side) | POT_WIPER |
| `POT_WIPER_ADC` | Potentiometer wiper (ADS1015 side, after series R) | POT_WIPER_ADC |
| `BTN1_IN` | Button 1 | BTN1_IN, BTN2_IN, BTN3_IN |
| `HALF_NUT_IN` | Half-nut switch | HALF_NUT_IN |
| `LIM_Z_PLUS_IN` | Limit Z+ | LIM_Z_PLUS_IN, LIM_Z_MINUS_IN, LIM_X_PLUS_IN, LIM_X_MINUS_IN |
| `I2C_SDA` | I2C data | I2C_SDA |
| `I2C_SCL` | I2C clock | I2C_SCL |
| `ESTOP_IN` | E-Stop software | ESTOP_IN, ESTOP_NC, ESTOP_COM |
| `SW_5V` | Buck switch node | SW_5V |
| `BOOT_5V` | Buck bootstrap | BOOT_5V |
| `FB_5V` | Buck feedback | FB_5V |
| `RT_CT` | Buck timer | RT_CT |

---

## 22. PCB Layout Tips

### Layer Stack (2-layer recommended)

| Layer | Usage |
|-------|-------|
| Top | Components, signal routing, power traces |
| Bottom | GND plane (solid, unbroken — pour entire layer) |

### Placement Guidelines

1. **RPi GPIO header (J1)** — Center of board, aligned with standard HAT mounting holes (4× M2.5 at 48.8×33.5 mm)
2. **74HC245 (U1)** — Close to GPIO header (short 3.3V traces from RPi)
3. **ADS1015 (U2)** — Close to potentiometer connector (J7), keep analog traces away from digital noise
4. **Buck regulator (U3)** — Near DC jack (J17), keep SW node trace short and away from sensitive signals
5. **LDO (U4)** — Near buck output or 12V input, with thermal pad connected to GND plane
6. **All screw terminals** — Edge of board, grouped by function (buttons together, limits together)
8. **JST connectors** — Edge of board, oriented for cable exit (toward lathe machine)

### Critical Trace Rules

| Rule | Detail |
|------|--------|
| **SW node (buck)** | Keep trace < 10 mm, no vias, keep away from I2C/encoder traces |
| **I2C (SDA/SCL)** | Keep < 5 cm, route over GND plane, no splits underneath |
| **Encoder signals** | Differential-pair-like routing (A and B traces same length, close together), keep away from motor signals |
| **STEP signals (5V side)** | Short and direct from 74HC245 to connector, with series resistor near 74HC245 |
| **3.3V analog (ADS1015)** | Keep 3V3 trace to ADS1015 away from digital switching noise |
| **Power traces** | 5V0 and 3V3: minimum 1 mm width (carries ~200 mA). VIN_12V: minimum 1.5 mm width |

### Via Strategy

- Decoupling cap vias: 1 via per cap, directly under cap pad if possible
- Power plane vias: 4+ vias connecting top 5V0/3V3 traces to bottom GND plane, near each regulator
- Signal vias: Minimize — route on top layer when possible

### Thermal

- AP2112 SOT-223 exposed pad: Connect to GND with multiple thermal vias (3+) to bottom GND plane
- MP2307: Keep copper clearance around SW pin (switching node — don't pour GND under it)
- Schottky diodes (SS34, SMA package): Adequate for expected currents (< 500 mA each)

---

*Document generated from `config.py`, `HARDWARE.md`, `PCB_HAT_Design.md`, and HAL interface code.*
*Updated: 2026-08-06 — 12V DC jack on HAT only, RPi native USB-C, 74HC245, full KiCad library references, capacitor placement guide.*
