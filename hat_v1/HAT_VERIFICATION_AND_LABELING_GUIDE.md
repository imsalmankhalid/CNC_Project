# MbW Lathe HAT – Design Verification & Connector Labeling Guide
**Date:** 2026-08-11  
**Purpose:** Comprehensive verification of HAT design against lathe_rpi project requirements  
**Status:** ⚠️ ISSUES FOUND – Action Required Before Fabrication  

---

## Executive Summary

✅ **GOOD:** Core functionality implemented (level shifters, ADC, connectors)  
⚠️ **ISSUES:** DRC violations, connector labeling confusion, missing protection components  
📋 **ACTION REQUIRED:** Fix DRC errors, relabel connectors, verify protection circuits  

---

## Part 1: Current HAT Connector Inventory

### Connectors Found in Schematic (`hat.kicad_sch`)

| Ref | Current Label | Footprint | Pin Count | Verified Purpose |
|-----|---------------|-----------|-----------|------------------|
| **J1** | "GPIO" | `PinSocket_2x20_P2.54mm_Vertical` | 40-pin (2×20) | ✅ Raspberry Pi GPIO Header |
| **J2** | "x axis motor" | `TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03` | 3-pin | ⚠️ **MISLABELED** – Should be X motor, but only 3 pins (needs 6-8) |
| **J3** | "Z axis motor" | `TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03` | 3-pin | ⚠️ **MISLABELED** – Should be Z motor, but only 3 pins (needs 6-8) |
| **J4** | "x axis enc" | `TerminalBlock_Phoenix_MPT-0,5-4-2.54_1x04` | 4-pin | ⚠️ Encoder (but labeled as X, should verify nets) |
| **J5** | "z axis enc" | `TerminalBlock_Phoenix_MPT-0,5-4-2.54_1x04` | 4-pin | ⚠️ Encoder (but labeled as Z, should verify nets) |
| **J6** | "Pot" | `Screw_Terminal_01x03` | 3-pin | ✅ Potentiometer (correct) |
| **J7** | "Limit switches" | `Screw_Terminal_01x04` | 4-pin | ❌ **INSUFFICIENT** – Needs 8 pins (4 switches × 2 pins) |
| **J9** | "Barrel_Jack_Switch" | Barrel Jack | 3-pin | ✅ 12V DC Power Input |

### Missing Connectors (Expected but NOT Found)

| Expected Connector | Purpose | Required Pins | Status |
|-------------------|---------|---------------|--------|
| **Buttons** | 3× push buttons (BTN1, BTN2, BTN3) | 6 pins (3×2) or 3× 2-pin | ❌ **MISSING** |
| **Half-Nut Switch** | Half-nut engagement sensor | 2 pins | ❌ **MISSING** |
| **Spindle Index** | Spindle RPM sensor (AutoTech C3) | 3 pins (VCC, GND, SIGNAL) | ❌ **MISSING** |

---

## Part 2: Critical Issues & Discrepancies

### Issue 1: Motor Connectors Under-Pinned ⚠️

**Problem:** J2 and J3 are labeled as motor connectors but only have 3 pins each.

**Required Pins for ClearPath Servo:**
```
Pin 1: STEP (5V TTL)
Pin 2: DIR (5V TTL)
Pin 3: ENABLE (5V TTL)
Pin 4: HLFB (Hardware Feedback) – optional, can leave unconnected
Pin 5: GND (Signal ground)
Pin 6: +5V (Logic power for servo)
Pin 7: (HV+ 70V) – supplied externally, NOT on HAT
Pin 8: (HV- 70V) – supplied externally, NOT on HAT
```

**Minimum Required:** 6 pins (STEP, DIR, ENABLE, HLFB, GND, +5V)  
**Acceptable Reduced:** 5 pins (STEP, DIR, ENABLE, GND, +5V) if HLFB not used  

**Action Required:**
- Change J2 and J3 to **6-pin or 8-pin** terminal blocks or headers
- Recommended: `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06_P2.54mm_Horizontal` (6-pin)
- OR use Molex KK-254 1×6 headers for cleaner connections

### Issue 2: Limit Switch Connector Insufficient ❌

**Problem:** J7 is labeled "Limit switches" but only has 4 pins.

**Required:** 4 limit switches × 2 pins each = **8 pins total**
- Limit Z+ (GPIO 16) + GND
- Limit Z− (GPIO 7) + GND
- Limit X+ (GPIO 8) + GND
- Limit X− (GPIO 11) + GND

**Action Required:**
- Change J7 to **8-pin** terminal block: `TerminalBlock_Phoenix_MPT-0,5-8-2.54_1x08_P2.54mm_Horizontal`
- OR use 4× separate 2-pin terminal blocks (more modular for field wiring)

### Issue 3: Missing Connectors for Buttons, Half-Nut, Spindle ❌

**Problem:** No connectors found for:
- 3× Push buttons (GPIO 26, 20, 21)
- 1× Half-nut switch (GPIO 4)
- 1× Spindle index sensor (GPIO 12)

**Action Required:** Add the following connectors:

| New Ref | Label | Pins | Footprint | Purpose |
|---------|-------|------|-----------|---------|
| **J8** | "Push Buttons" | 6-pin (3×2) or 8-pin | `TerminalBlock_Phoenix_MPT-0,5-6-2.54` | BTN1, BTN2, BTN3 (each + GND) |
| **J10** | "Half-Nut Switch" | 2-pin | `TerminalBlock_Phoenix_MPT-0,5-2-2.54` | Half-nut sensor |
| **J11** | "Spindle Index" | 3-pin | `Connector_JST:JST_PH_3Pin_2.00mm_Pitch` | AutoTech C3 sensor (VCC, GND, SIGNAL) |

**Alternative:** Use a single **10-pin** terminal block for all inputs (buttons + half-nut + spare), labeled "Digital Inputs"

### Issue 4: Encoder Connector Labels Swapped? ⚠️

**Problem:** J4 is labeled "x axis enc" and J5 is labeled "z axis enc"

**Expected GPIO Mapping (from `config.py`):**
```
GPIO_Z_ENC_A  = 5   (RPi Pin 29)
GPIO_Z_ENC_B  = 6   (RPi Pin 31)
GPIO_X_ENC_A  = 13  (RPi Pin 33)
GPIO_X_ENC_B  = 19  (RPi Pin 35)
```

**Action Required:** Verify schematic nets:
- J4 should connect to GPIO 13 & 19 (X encoder)
- J5 should connect to GPIO 5 & 6 (Z encoder)
- If nets are correct, labels are correct
- If nets are swapped, either fix the nets OR swap the labels

**Recommended Verification:** Trace nets from J4/J5 back to J1 (GPIO header) and confirm against table above.

---

## Part 3: Connector Labeling Recommendations

### Proposed Connector Naming Convention

Use **functional names** that match the lathe_rpi software and wiring harness:

| Ref | **NEW Label** | Function | Pins | External Connection |
|-----|---------------|----------|------|---------------------|
| **J1** | `"RPi GPIO Header"` | Main interface | 40 | Raspberry Pi 40-pin GPIO |
| **J2** | `"X Motor (ClearPath)"` | X-axis servo signals | 6 | X-axis ClearPath SDSK |
| **J3** | `"Z Motor (ClearPath)"` | Z-axis servo signals | 6 | Z-axis ClearPath SDSK |
| **J4** | `"X Encoder (AMT103)"` | X-axis encoder | 4 | X-axis handwheel encoder |
| **J5** | `"Z Encoder (AMT103)"` | Z-axis encoder | 4 | Z-axis handwheel encoder |
| **J6** | `"Potentiometer (Feed Rate)"` | Feed rate control | 3 | 10kΩ pot dial |
| **J7** | `"Limit Switches (4×)"` | Axis limit sensors | 8 | Z+, Z−, X+, X− switches |
| **J8** | `"Push Buttons (3×)"` | Manual controls | 6 | BTN1, BTN2, BTN3 |
| **J9** | `"12V DC Power Input"` | Power supply | 3 | 12V barrel jack |
| **J10** | `"Half-Nut Switch"` | Half-nut sensor | 2 | Half-nut lever switch |
| **J11** | `"Spindle Index (C3)"` | Spindle RPM sensor | 3 | AutoTech C3 optical |

### Silkscreen Labeling Best Practices

For each connector, add the following on the **F.Silkscreen** layer:

1. **Reference Designator** (J1, J2, etc.) – large, bold
2. **Functional Name** (as listed above) – medium size
3. **Pin Numbers** (1, 2, 3...) – small, next to each pin
4. **Pin 1 Indicator** – square pad, triangle, or dot
5. **Signal Names** (optional, if space permits):
   - Example for J2 (X Motor): `STEP DIR EN GND 5V`
   - Example for J5 (Z Encoder): `A B +3V3 GND`

### Silkscreen Text Size Guidelines

| Element | Text Height | Stroke Width | Example |
|---------|-------------|--------------|---------|
| Reference (J1) | 1.5 mm | 0.3 mm | **J1** |
| Functional name | 1.0 mm | 0.2 mm | RPi GPIO |
| Pin numbers | 0.7 mm | 0.15 mm | 1 2 3 |
| Signal names | 0.8 mm | 0.15 mm | STEP DIR |

---

## Part 4: Pin-by-Pin Connector Specifications

### J1 – RPi GPIO Header (40-pin, 2×20)
```
Standard Raspberry Pi HAT header – DO NOT modify
See: lathe_rpi/HARDWARE.md Table "GPIO Pin Assignment Table"
```

### J2 – X Motor (ClearPath) – **6-pin Terminal Block**
```
Pin 1: X_STEP    (from 74HC245 B4 via 100Ω) – 5V TTL
Pin 2: X_DIR     (from 74HC245 B5 via 100Ω) – 5V TTL
Pin 3: X_ENABLE  (from 74HC245 B6 direct) – 5V TTL
Pin 4: GND       (signal ground)
Pin 5: +5V       (logic power, from 5V0 rail)
Pin 6: HLFB_X    (optional feedback – leave unconnected or tie to GND)
```

### J3 – Z Motor (ClearPath) – **6-pin Terminal Block**
```
Pin 1: Z_STEP    (from 74HC245 B1 via 100Ω) – 5V TTL
Pin 2: Z_DIR     (from 74HC245 B2 via 100Ω) – 5V TTL
Pin 3: Z_ENABLE  (from 74HC245 B3 direct) – 5V TTL
Pin 4: GND       (signal ground)
Pin 5: +5V       (logic power, from 5V0 rail)
Pin 6: HLFB_Z    (optional feedback – leave unconnected or tie to GND)
```

### J4 – X Encoder (AMT103) – **4-pin Terminal Block**
```
Pin 1: +3V3      (encoder power, 3.3V rail)
Pin 2: GND       (ground)
Pin 3: ENC_A     (to GPIO 13 via 10kΩ pull-up)
Pin 4: ENC_B     (to GPIO 19 via 10kΩ pull-up)

Note: AMT103-V INDEX output not used (software doesn't track index)
```

### J5 – Z Encoder (AMT103) – **4-pin Terminal Block**
```
Pin 1: +3V3      (encoder power, 3.3V rail)
Pin 2: GND       (ground)
Pin 3: ENC_A     (to GPIO 5 via 10kΩ pull-up)
Pin 4: ENC_B     (to GPIO 6 via 10kΩ pull-up)
```

### J6 – Potentiometer (Feed Rate) – **3-pin Terminal Block**
```
Pin 1: +5V       (pot rail A)
Pin 2: WIPER     (to ADS1115 AIN0 via 10kΩ series resistor)
Pin 3: GND       (pot rail B)

External: 10kΩ linear pot, Bourns 3547S-1AA-103A or similar
```

### J7 – Limit Switches – **8-pin Terminal Block**
```
Pin 1: LIM_Z+    (to GPIO 16 via 10kΩ pull-up, active LOW)
Pin 2: GND
Pin 3: LIM_Z−    (to GPIO 7 via 10kΩ pull-up, active LOW)
Pin 4: GND
Pin 5: LIM_X+    (to GPIO 8 via 10kΩ pull-up, active LOW)
Pin 6: GND
Pin 7: LIM_X−    (to GPIO 11 via 10kΩ pull-up, active LOW)
Pin 8: GND

Switch Type: Normally-Open (NO), closes to GND when triggered
```

### J8 – Push Buttons (3×) – **6-pin Terminal Block**
```
Pin 1: BTN1      (to GPIO 26 via 10kΩ pull-up, active LOW)
Pin 2: GND
Pin 3: BTN2      (to GPIO 20 via 10kΩ pull-up, active LOW)
Pin 4: GND
Pin 5: BTN3      (to GPIO 21 via 10kΩ pull-up, active LOW)
Pin 6: GND

Switch Type: Momentary push buttons, NO contact
```

### J9 – 12V DC Power Input – **Barrel Jack (5.5×2.1mm)**
```
Center Pin (+): VIN_12V_RAW  (12V DC input, center-positive)
Sleeve (−):     GND

Input Protection:
  - F1 (1A fuse) on VIN line
  - D8 (SMAJ13CA TVS) across VIN to GND
  - C7 (10µF bulk) + C8 (100nF decoupling)
```

### J10 – Half-Nut Switch – **2-pin Terminal Block**
```
Pin 1: HALF_NUT  (to GPIO 4 via 10kΩ pull-down, active HIGH)
Pin 2: GND

Switch Type: SPST lever switch, closes to +3V3 when engaged
(Or: use NO switch to GND with pull-up, active LOW – check config.py)
```

### J11 – Spindle Index (AutoTech C3) – **3-pin JST-PH or Terminal Block**
```
Pin 1: +5V       (sensor power, from 5V0 rail)
Pin 2: GND       (ground)
Pin 3: SIGNAL    (5V TTL pulse → voltage divider → GPIO 12)

Voltage Divider (on HAT):
  5V TTL ──[R7: 10kΩ]──┬──[R8: 20kΩ]── GND
                       │
                    GPIO 12 (≈3.33V)
```

---

## Part 5: Missing Components Verification

### Protection Components (from PCB_HAT_Design.md Spec)

| Component | Purpose | Qty | Part Number | Status |
|-----------|---------|-----|-------------|--------|
| **TVS Diodes (Motor)** | ESD protection on STEP/DIR/ENABLE | 6 | PESD5V0S1UL (SOD-323) | ❓ **VERIFY** |
| **TVS Diode (Spindle)** | ESD protection on spindle index | 1 | PESD5V0S1UL (SOD-323) | ❓ **VERIFY** |
| **PTC Fuse** | 5V rail protection (from RPi) | 1 | 500mA resettable | ❓ **VERIFY** |
| **Series Resistors** | STEP signal integrity | 2 | 100Ω (0805) – R5, R6 found ✓ | ✅ R5, R6 = 10kΩ (wrong value?) |

**Action Required:**
1. Search schematic for TVS diodes on motor signal lines (D1–D6?)
2. Search for TVS on spindle input line
3. Verify PTC fuse on 5V rail from J1 Pin 2/4
4. Check R5/R6 values – spec says 100Ω but schematic shows 10kΩ

### Pull-up/Pull-down Resistors

Expected from design spec:

| Signal Group | Qty | Value | Purpose | Status |
|--------------|-----|-------|---------|--------|
| Encoder pull-ups | 4 | 10kΩ | Z_ENC_A/B, X_ENC_A/B | ⚠️ May be in AMT103 internally |
| Button pull-ups | 3 | 10kΩ | BTN1, BTN2, BTN3 | ❓ **VERIFY** |
| Limit pull-ups | 4 | 10kΩ | LIM_Z+/−, LIM_X+/− | ❓ **VERIFY** |
| Half-nut pull-down | 1 | 10kΩ | GPIO 4 | ❓ **VERIFY** |
| I2C pull-ups | 2 | 4.7kΩ | SDA, SCL | ❓ **VERIFY** (may be on ADS1115) |

**Action Required:** Verify all pull resistors exist in schematic. Check components R1-R20 for these functions.

### Status LEDs (Optional but Recommended)

| LED | Color | Purpose | Resistor | Status |
|-----|-------|---------|----------|--------|
| PWR | Green | 5V rail active | 330Ω | ❓ **VERIFY** |
| 3V3 | Blue/Yellow | 3.3V rail active | 330Ω | ❓ **VERIFY** |
| ACT | Yellow | STEP pulse activity | 330Ω | ❓ **VERIFY** |

**Action Required:** Search for LED components in schematic. If missing, recommend adding for debug.

---

## Part 6: Schematic Net Verification Checklist

### Critical Nets to Verify

Before fabrication, manually trace these nets in KiCad schematic:

| Net Name | From | To | Expected GPIO |
|----------|------|-----|---------------|
| `Z_STEP_3V3` | J1 Pin 11 | 74HC245 U3/U4 A1 | GPIO 17 ✓ |
| `Z_STEP_5V` | 74HC245 B1 | R5 → J3 Pin 1 | — |
| `Z_DIR_3V3` | J1 Pin 13 | 74HC245 A2 | GPIO 27 ✓ |
| `Z_DIR_5V` | 74HC245 B2 | R6? → J3 Pin 2 | — |
| `Z_EN_3V3` | J1 Pin 15 | 74HC245 A3 | GPIO 22 ✓ |
| `Z_EN_5V` | 74HC245 B3 | J3 Pin 3 | — |
| `X_STEP_3V3` | J1 Pin 18 | 74HC245 A4 | GPIO 24 ✓ |
| `X_STEP_5V` | 74HC245 B4 | J2 Pin 1 | — |
| `X_DIR_3V3` | J1 Pin 16 | 74HC245 A5 | GPIO 23 ✓ |
| `X_DIR_5V` | 74HC245 B5 | J2 Pin 2 | — |
| `X_EN_3V3` | J1 Pin 22 | 74HC245 A6 | GPIO 25 ✓ |
| `X_EN_5V` | 74HC245 B6 | J2 Pin 3 | — |
| `Z_ENC_A` | J1 Pin 29 | J5 Pin 3 | GPIO 5 ✓ |
| `Z_ENC_B` | J1 Pin 31 | J5 Pin 4 | GPIO 6 ✓ |
| `X_ENC_A` | J1 Pin 33 | J4 Pin 3 | GPIO 13 ✓ |
| `X_ENC_B` | J1 Pin 35 | J4 Pin 4 | GPIO 19 ✓ |
| `POT_WIPER` | J6 Pin 2 | 10kΩ → ADS1115 AIN0 | — |
| `SPINDLE_RAW` | J11 Pin 3 | Voltage divider → GPIO 12 | GPIO 12 ✓ |
| `BTN1` | J8 Pin 1 | J1 Pin 37 | GPIO 26 ✓ |
| `BTN2` | J8 Pin 3 | J1 Pin 38 | GPIO 20 ✓ |
| `BTN3` | J8 Pin 5 | J1 Pin 40 | GPIO 21 ✓ |
| `HALF_NUT` | J10 Pin 1 | J1 Pin 7 | GPIO 4 ✓ |
| `LIM_Z+` | J7 Pin 1 | J1 Pin 36 | GPIO 16 ✓ |
| `LIM_Z−` | J7 Pin 3 | J1 Pin 26 | GPIO 7 ✓ |
| `LIM_X+` | J7 Pin 5 | J1 Pin 24 | GPIO 8 ✓ |
| `LIM_X−` | J7 Pin 7 | J1 Pin 23 | GPIO 11 ✓ |

**Action:** Use KiCad's "Highlight Net" feature to trace each net and verify connections.

---

## Part 7: DRC (Design Rule Check) Issues

### From DRC_Analysis_and_Resolution.md

**CRITICAL – Must Fix Before Ordering:**

1. **Clearance Violation** at (123.843, 53.672)
   - Via on `/P5V` net too close to track on `Net-(Q2A-B1)`
   - Gap: 0.177 mm (required: 0.200 mm)
   - **FIX:** Move via 0.05 mm away from track

2. **Silkscreen Overlap #1:** R7 reference overlaps R5 body
   - **FIX:** Move R5, R6, R7 reference text to right side of resistors

3. **Silkscreen Overlap #2:** R5 reference overlaps R6 body
   - **FIX:** Same as above

**See:** `hat/DRC_QUICK_REFERENCE.md` for fix procedures.

---

## Part 8: Action Items Summary

### CRITICAL (Must Do Before Fabrication)

- [ ] **Fix DRC clearance violation** at via (123.843, 53.672)
- [ ] **Fix silkscreen overlaps** for R5, R6, R7
- [ ] **Add missing connectors:**
  - [ ] J8: Push buttons (6-pin)
  - [ ] J10: Half-nut switch (2-pin)
  - [ ] J11: Spindle index (3-pin JST or terminal block)
- [ ] **Expand J7** from 4-pin to 8-pin (limit switches)
- [ ] **Expand J2 and J3** from 3-pin to 6-pin (motor signals)
- [ ] **Verify all TVS diodes** are present on signal lines
- [ ] **Verify PTC fuse** on 5V rail from RPi
- [ ] **Check resistor values:**
  - [ ] R5, R6 should be 100Ω (currently 10kΩ?)
  - [ ] R7, R8 voltage divider (10kΩ, 20kΩ for spindle)

### HIGH PRIORITY (Should Do)

- [ ] **Relabel all connectors** with functional names (see Part 3)
- [ ] **Add pin 1 indicators** on all connectors (square pad or triangle)
- [ ] **Add pin numbers** on silkscreen next to each connector
- [ ] **Add signal names** on silkscreen (STEP, DIR, EN, etc.)
- [ ] **Verify all pull-up/pull-down resistors** exist
- [ ] **Add status LEDs** (PWR, 3V3, ACT)
- [ ] **Add test points** (TP_3V3, TP_5V, TP_GND, TP_STEP_Z, TP_STEP_X)

### MEDIUM PRIORITY (Nice to Have)

- [ ] Add HAT ID EEPROM (AT24C32 on I2C 0x50)
- [ ] Add fiducials for pick-and-place
- [ ] Add version number and date on back silkscreen
- [ ] Add polarity marking on 12V jack (+ and −)
- [ ] Add thermal vias under regulators (MP2307, AP2112/L7805)
- [ ] Add ground plane stitching vias

---

## Part 9: Recommended Connector Pinout Silkscreen Labels

Use these exact labels on the PCB silkscreen for each connector:

### J1 (RPi GPIO Header)
```
Silkscreen Text (top):
┌─────────────────────┐
│   RPi GPIO Header   │
│        J1           │
│   40-Pin (2×20)     │
└─────────────────────┘
Pin 1 indicator: Square pad + triangle
```

### J2 (X Motor)
```
Silkscreen Text:
┌──────────────────────┐
│  X Motor (ClearPath) │
│         J2           │
└──────────────────────┘
Pin Labels (next to pins):
 1  2  3  4  5  6
 ST DR EN GN 5V HF
```

### J3 (Z Motor)
```
Silkscreen Text:
┌──────────────────────┐
│  Z Motor (ClearPath) │
│         J3           │
└──────────────────────┘
Pin Labels:
 1  2  3  4  5  6
 ST DR EN GN 5V HF
```

### J4 (X Encoder)
```
Silkscreen Text:
┌───────────────────────┐
│  X Encoder (AMT103)   │
│         J4            │
└───────────────────────┘
Pin Labels:
 1   2   3  4
 3V3 GND A  B
```

### J5 (Z Encoder)
```
Silkscreen Text:
┌───────────────────────┐
│  Z Encoder (AMT103)   │
│         J5            │
└───────────────────────┘
Pin Labels:
 1   2   3  4
 3V3 GND A  B
```

### J6 (Potentiometer)
```
Silkscreen Text:
┌─────────────────────────┐
│  Pot (Feed Rate)        │
│         J6              │
└─────────────────────────┘
Pin Labels:
 1   2      3
 5V  WIPER  GND
```

### J7 (Limit Switches)
```
Silkscreen Text:
┌────────────────────────┐
│  Limit Switches (4×)   │
│         J7             │
└────────────────────────┘
Pin Labels:
 1    2   3    4   5    6   7    8
 Z+   G   Z-   G   X+   G   X-   G
```

### J8 (Push Buttons)
```
Silkscreen Text:
┌────────────────────────┐
│  Push Buttons (3×)     │
│         J8             │
└────────────────────────┘
Pin Labels:
 1    2   3    4   5    6
 BT1  G   BT2  G   BT3  G
```

### J9 (12V Power)
```
Silkscreen Text (next to barrel jack):
┌────────────────────┐
│  12V DC Power      │
│       J9           │
│    (+ CENTER)      │
└────────────────────┘
Add: (+) symbol near center pin
     (−) symbol near sleeve
```

### J10 (Half-Nut)
```
Silkscreen Text:
┌────────────────────┐
│  Half-Nut Switch   │
│       J10          │
└────────────────────┘
Pin Labels:
 1    2
 HN   G
```

### J11 (Spindle Index)
```
Silkscreen Text:
┌────────────────────┐
│  Spindle (C3)      │
│       J11          │
└────────────────────┘
Pin Labels:
 1   2    3
 5V  GND  SIG
```

---

## Part 10: Final Verification Before Ordering PCBs

### Pre-Fabrication Checklist

**Schematic:**
- [ ] All connectors added (J1–J11)
- [ ] All nets traced and verified against GPIO table
- [ ] All protection components present (TVS, PTC, fuse)
- [ ] All pull-up/pull-down resistors present
- [ ] Correct resistor values (100Ω for STEP series, 10kΩ/20kΩ for divider)
- [ ] Level shifter (74HC245) power and control pins correct
- [ ] ADC (ADS1115) power and I2C connections correct
- [ ] Power OR-ing diodes present (D11, D12, D14, D15)
- [ ] Decoupling caps on all ICs (<5mm from power pins)

**PCB Layout:**
- [ ] DRC run with ZERO errors
- [ ] All silkscreen labels added per Part 9
- [ ] Pin 1 indicators on all connectors
- [ ] Polarity markings on power connectors
- [ ] Test points added (TP_3V3, TP_5V, TP_GND)
- [ ] Thermal vias under regulators
- [ ] Ground plane stitching vias every 10-15mm
- [ ] Fiducials added (3×, opposite corners + center)
- [ ] Version number and date on back silkscreen
- [ ] All components ≥3mm from board edge
- [ ] Mounting holes have ≥5mm keepout zone

**Documentation:**
- [ ] Generate PDF schematics for reference
- [ ] Generate Gerber files
- [ ] Generate BOM with part numbers
- [ ] Generate pick-and-place file (if SMT assembly)
- [ ] Export drill file
- [ ] Create assembly drawing with connector pinouts

**Final Check:**
- [ ] Compare schematic against `lathe_rpi/config.py` GPIO assignments
- [ ] Compare schematic against `lathe_rpi/HARDWARE.md` specifications
- [ ] Compare schematic against `lathe_rpi/PCB_HAT_Design.md` requirements
- [ ] Review all DRC fixes applied
- [ ] Peer review by second person (if available)

---

## Part 11: Post-Fabrication Testing Plan

When the HAT arrives, test in this order (DO NOT connect to motors/encoders yet):

1. **Visual Inspection**
   - [ ] Check for solder bridges
   - [ ] Check for missing components
   - [ ] Check polarity of diodes, LEDs, electrolytic caps

2. **Power-Up Test (No RPi)**
   - [ ] Connect 12V power supply
   - [ ] Measure 5V0 rail (should be 4.8–5.2V)
   - [ ] Measure 3V3 rail (should be 3.2–3.4V)
   - [ ] Check for excessive heat on regulators

3. **RPi Connection Test (No 12V)**
   - [ ] Mount HAT on RPi
   - [ ] Power RPi via USB-C only
   - [ ] Verify 5V0 and 3V3 rails present (back-fed from RPi)
   - [ ] Run `i2cdetect -y 1` to verify ADS1115 at 0x48

4. **GPIO Test**
   - [ ] Run `lathe_rpi/test/gpio_test.py` to verify:
     - [ ] Button inputs read correctly
     - [ ] Limit switch inputs read correctly
     - [ ] Encoder inputs respond to rotation
     - [ ] Step/dir outputs toggle correctly

5. **ADC Test**
   - [ ] Connect potentiometer to J6
   - [ ] Verify ADC reads pot position (0–1023)

6. **Motor Test (CAUTION: Motors will move)**
   - [ ] Connect encoders to J4, J5
   - [ ] Connect motors to J2, J3 (70V power OFF initially)
   - [ ] Apply 70V motor power
   - [ ] Run `lathe_rpi/test/enc_drive_motor.py`
   - [ ] Verify motors follow handwheel rotation

7. **Full Integration Test**
   - [ ] Run `lathe_rpi/main.py`
   - [ ] Verify UI displays correctly
   - [ ] Test all modes (Standard, Threading, Profile, Radius)
   - [ ] Test limit switches (E-stop when triggered)

---

## Appendix A: Quick Reference – Connector Summary Table

| Ref | Label | Pins | Type | GPIO/Signals |
|-----|-------|------|------|-------------|
| J1 | RPi GPIO Header | 40 | Socket 2×20 | All RPi GPIO |
| J2 | X Motor (ClearPath) | 6 | Terminal | X_STEP, X_DIR, X_EN, GND, 5V, HLFB |
| J3 | Z Motor (ClearPath) | 6 | Terminal | Z_STEP, Z_DIR, Z_EN, GND, 5V, HLFB |
| J4 | X Encoder (AMT103) | 4 | Terminal | GPIO 13, 19, 3V3, GND |
| J5 | Z Encoder (AMT103) | 4 | Terminal | GPIO 5, 6, 3V3, GND |
| J6 | Potentiometer | 3 | Terminal | ADS1115 AIN0, 5V, GND |
| J7 | Limit Switches (4×) | 8 | Terminal | GPIO 16, 7, 8, 11, GND×4 |
| J8 | Push Buttons (3×) | 6 | Terminal | GPIO 26, 20, 21, GND×3 |
| J9 | 12V DC Power | 3 | Barrel Jack | VIN_12V, GND |
| J10 | Half-Nut Switch | 2 | Terminal | GPIO 4, GND |
| J11 | Spindle Index (C3) | 3 | JST or Terminal | GPIO 12 (via divider), 5V, GND |

---

## Appendix B: GPIO Pin Mapping Reference

| GPIO (BCM) | RPi Pin | Function | HAT Connector | Notes |
|------------|---------|----------|---------------|-------|
| 2 | 3 | I2C SDA | — | ADS1115 on-board |
| 3 | 5 | I2C SCL | — | ADS1115 on-board |
| 4 | 7 | Half-Nut | J10 Pin 1 | Active HIGH (pull-down) |
| 5 | 29 | Z Enc A | J5 Pin 3 | Quadrature A |
| 6 | 31 | Z Enc B | J5 Pin 4 | Quadrature B |
| 7 | 26 | Limit Z− | J7 Pin 3 | Active LOW (pull-up, NC) |
| 8 | 24 | Limit X+ | J7 Pin 5 | Active LOW (pull-up, NC) |
| 11 | 23 | Limit X− | J7 Pin 7 | Active LOW (pull-up, NC) |
| 12 | 32 | Spindle | J11 Pin 3 | Via voltage divider |
| 13 | 33 | X Enc A | J4 Pin 3 | Quadrature A |
| 16 | 36 | Limit Z+ | J7 Pin 1 | Active LOW (pull-up, NC) |
| 17 | 11 | Z STEP | J3 Pin 1 | Via 74HC245 + 100Ω |
| 19 | 35 | X Enc B | J4 Pin 4 | Quadrature B |
| 20 | 38 | Button 2 | J8 Pin 3 | Active LOW (pull-up) |
| 21 | 40 | Button 3 | J8 Pin 5 | Active LOW (pull-up) |
| 22 | 15 | Z ENABLE | J3 Pin 3 | Via 74HC245 |
| 23 | 16 | X DIR | J2 Pin 2 | Via 74HC245 + 100Ω |
| 24 | 18 | X STEP | J2 Pin 1 | Via 74HC245 + 100Ω |
| 25 | 22 | X ENABLE | J2 Pin 3 | Via 74HC245 |
| 26 | 37 | Button 1 | J8 Pin 1 | Active LOW (pull-up) |
| 27 | 13 | Z DIR | J3 Pin 2 | Via 74HC245 + 100Ω |

---

## Document Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-08-11 | 1.0 | Initial verification document created |

---

**END OF VERIFICATION GUIDE**
