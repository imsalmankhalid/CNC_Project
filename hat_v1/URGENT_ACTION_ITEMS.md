# MbW Lathe HAT – URGENT ACTION ITEMS
**Date:** 2026-08-11  
**Status:** ⚠️ PCB NOT READY FOR FABRICATION  

---

## 🚨 CRITICAL ISSUES (Must Fix Before Ordering)

### 1. DRC Violations ❌
- **Clearance violation** at via (123.843, 53.672) – 0.023mm too close
  - **Fix:** Move via 0.1mm away from track
- **Silkscreen overlaps** – R5, R6, R7 reference text overlaps resistor bodies
  - **Fix:** Move reference text to right side or reduce font size

### 2. Missing Connectors ❌
Current schematic has only 8 connectors (J1-J7, J9). Missing:
- **J8:** Push buttons (3× buttons, needs 6 pins)
- **J10:** Half-nut switch (needs 2 pins)
- **J11:** Spindle index sensor (needs 3 pins)

### 3. Insufficient Connector Pin Counts ⚠️
- **J2 & J3** (Motors): Currently 3-pin, needs **6-pin** each
  - Required: STEP, DIR, ENABLE, GND, +5V, HLFB
- **J7** (Limits): Currently 4-pin, needs **8-pin**
  - Required: 4 switches × 2 pins (signal + GND)

### 4. Connector Labels Confusing ⚠️
- J2 labeled "x axis motor" but J3 labeled "Z axis motor"
- J4 labeled "x axis enc" but J5 labeled "z axis enc"
- Need to verify nets match labels

---

## 📋 IMMEDIATE ACTION CHECKLIST

### Step 1: Fix DRC Errors (30 minutes)
- [ ] Open `hat.kicad_pcb` in KiCad
- [ ] Navigate to via at (123.843, 53.672)
- [ ] Move via 0.1mm away from track (any direction)
- [ ] Move R5, R6, R7 reference text to right side
- [ ] Run DRC → Verify ZERO errors

### Step 2: Add Missing Connectors (1 hour)
- [ ] Add **J8** (6-pin terminal block) – Push buttons
  - Footprint: `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06`
  - Nets: BTN1 (GPIO 26), GND, BTN2 (GPIO 20), GND, BTN3 (GPIO 21), GND
- [ ] Add **J10** (2-pin terminal block) – Half-nut switch
  - Footprint: `TerminalBlock_Phoenix_MPT-0,5-2-2.54_1x02`
  - Nets: HALF_NUT (GPIO 4), GND
- [ ] Add **J11** (3-pin JST or terminal) – Spindle index
  - Footprint: `Connector_JST:JST_PH_3Pin_2.00mm_Pitch` OR `TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03`
  - Nets: +5V, GND, SPINDLE_RAW → voltage divider → GPIO 12

### Step 3: Expand Existing Connectors (1 hour)
- [ ] Change **J2** from 3-pin to 6-pin terminal block
  - Add pins: GND, +5V, HLFB (can leave HLFB unconnected)
- [ ] Change **J3** from 3-pin to 6-pin terminal block
  - Add pins: GND, +5V, HLFB (can leave HLFB unconnected)
- [ ] Change **J7** from 4-pin to 8-pin terminal block
  - Current: probably has 2 limit switches
  - Need: 4 limit switches (Z+, Z−, X+, X−) × 2 pins each

### Step 4: Verify Protection Components (30 minutes)
Check schematic for:
- [ ] **TVS diodes** (D1-D6) on motor STEP/DIR/ENABLE lines
- [ ] **TVS diode** (D7?) on spindle index input
- [ ] **PTC fuse** (F2?) on 5V rail from J1 Pin 2/4
- [ ] **Series resistors** R5, R6 should be **100Ω** (not 10kΩ!)

### Step 5: Verify Pull Resistors (30 minutes)
Check schematic for:
- [ ] **Button pull-ups** (3× 10kΩ) on GPIO 26, 20, 21
- [ ] **Limit pull-ups** (4× 10kΩ) on GPIO 16, 7, 8, 11
- [ ] **Half-nut pull-down** (1× 10kΩ) on GPIO 4
- [ ] **I2C pull-ups** (2× 4.7kΩ) on SDA, SCL
- [ ] **Encoder pull-ups** (4× 10kΩ) – may be internal to AMT103

### Step 6: Update Connector Labels (15 minutes)
Update silkscreen text on PCB:
- [ ] J1: "RPi GPIO Header"
- [ ] J2: "X Motor (ClearPath)"
- [ ] J3: "Z Motor (ClearPath)"
- [ ] J4: "X Encoder (AMT103)"
- [ ] J5: "Z Encoder (AMT103)"
- [ ] J6: "Potentiometer (Feed Rate)"
- [ ] J7: "Limit Switches (4×)"
- [ ] J8: "Push Buttons (3×)"
- [ ] J9: "12V DC Power Input"
- [ ] J10: "Half-Nut Switch"
- [ ] J11: "Spindle Index (C3)"

### Step 7: Add Silkscreen Details (30 minutes)
For each connector on PCB layout:
- [ ] Add pin numbers (1, 2, 3...) next to each pin
- [ ] Add pin 1 indicator (square pad or triangle)
- [ ] Add signal names if space permits (STEP, DIR, EN, A, B, etc.)
- [ ] Add polarity marking on J9 (12V jack): (+) and (−)

### Step 8: Final Verification (30 minutes)
- [ ] Run DRC → Confirm ZERO errors
- [ ] Run ERC (Electrical Rule Check) → Confirm ZERO errors
- [ ] Print schematic PDF → Visual review
- [ ] Print PCB layout PDF → Visual review
- [ ] Compare GPIO assignments vs `lathe_rpi/config.py`
- [ ] Generate BOM and verify all parts available

---

## 🔍 NET VERIFICATION – CRITICAL TRACES

Use KiCad "Highlight Net" to trace these connections:

| Net | From | To | GPIO | Status |
|-----|------|-----|------|--------|
| Z_STEP | J1 Pin 11 | 74HC245 A1 → B1 → J3 Pin 1 | GPIO 17 | ❓ |
| Z_DIR | J1 Pin 13 | 74HC245 A2 → B2 → J3 Pin 2 | GPIO 27 | ❓ |
| Z_ENABLE | J1 Pin 15 | 74HC245 A3 → B3 → J3 Pin 3 | GPIO 22 | ❓ |
| X_STEP | J1 Pin 18 | 74HC245 A4 → B4 → J2 Pin 1 | GPIO 24 | ❓ |
| X_DIR | J1 Pin 16 | 74HC245 A5 → B5 → J2 Pin 2 | GPIO 23 | ❓ |
| X_ENABLE | J1 Pin 22 | 74HC245 A6 → B6 → J2 Pin 3 | GPIO 25 | ❓ |
| Z_ENC_A | J1 Pin 29 | J5 Pin 3 | GPIO 5 | ❓ |
| Z_ENC_B | J1 Pin 31 | J5 Pin 4 | GPIO 6 | ❓ |
| X_ENC_A | J1 Pin 33 | J4 Pin 3 | GPIO 13 | ❓ |
| X_ENC_B | J1 Pin 35 | J4 Pin 4 | GPIO 19 | ❓ |

**If any net is WRONG, fix immediately!**

---

## 🛡️ PROTECTION CIRCUIT REQUIREMENTS

### Must Have:
- **Input fuse** (F1): 1A slow-blow on VIN_12V
- **TVS diode** (D8): SMAJ13CA on VIN_12V (transient protection)
- **Motor TVS** (D1-D6): PESD5V0S1UL on each STEP/DIR/ENABLE line
- **Spindle TVS** (D7): PESD5V0S1UL on spindle index input
- **PTC fuse**: 500mA on 5V rail from RPi (prevents backfeed overload)

### Recommended:
- **Status LEDs**: Power (green), 3V3 (blue), Activity (yellow)
- **Test points**: TP_3V3, TP_5V, TP_GND, TP_STEP_Z, TP_STEP_X

---

## 📦 CONNECTOR FOOTPRINT QUICK REFERENCE

| Connector | Current | Required | Footprint |
|-----------|---------|----------|-----------|
| J1 | 40-pin socket | ✅ OK | `PinSocket_2x20_P2.54mm_Vertical` |
| J2 (X Motor) | 3-pin term | ⚠️ 6-pin | `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06` |
| J3 (Z Motor) | 3-pin term | ⚠️ 6-pin | `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06` |
| J4 (X Enc) | 4-pin term | ✅ OK | `TerminalBlock_Phoenix_MPT-0,5-4-2.54_1x04` |
| J5 (Z Enc) | 4-pin term | ✅ OK | `TerminalBlock_Phoenix_MPT-0,5-4-2.54_1x04` |
| J6 (Pot) | 3-pin term | ✅ OK | `Screw_Terminal_01x03` |
| J7 (Limits) | 4-pin term | ⚠️ 8-pin | `TerminalBlock_Phoenix_MPT-0,5-8-2.54_1x08` |
| J8 (Buttons) | ❌ Missing | ➕ 6-pin | `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06` |
| J9 (12V) | Barrel jack | ✅ OK | `Barrel_Jack_Switch` |
| J10 (Half-Nut) | ❌ Missing | ➕ 2-pin | `TerminalBlock_Phoenix_MPT-0,5-2-2.54_1x02` |
| J11 (Spindle) | ❌ Missing | ➕ 3-pin | `JST_PH_3Pin_2.00mm` or `TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03` |

---

## ⏱️ ESTIMATED TIME TO FIX

| Task | Time | Difficulty |
|------|------|-----------|
| Fix DRC errors | 30 min | Easy |
| Add J8, J10, J11 connectors | 1 hour | Medium |
| Expand J2, J3, J7 connectors | 1 hour | Medium |
| Verify protection components | 30 min | Medium |
| Update connector labels | 30 min | Easy |
| Add silkscreen details | 30 min | Easy |
| Final verification | 30 min | Easy |
| **TOTAL** | **4-5 hours** | — |

---

## 📞 NEXT STEPS

1. **Review this document** and the full [HAT_VERIFICATION_AND_LABELING_GUIDE.md](HAT_VERIFICATION_AND_LABELING_GUIDE.md)
2. **Open KiCad** and start with DRC fixes (quick win)
3. **Add missing connectors** (J8, J10, J11)
4. **Expand insufficient connectors** (J2, J3, J7)
5. **Run full verification** using checklists in main guide
6. **Generate Gerbers** and double-check before ordering

---

## ❓ Questions to Answer Before Proceeding

1. **Are TVS diodes already in the schematic?** (Search for D1-D7)
2. **What is the value of R5 and R6?** (Should be 100Ω, not 10kΩ)
3. **Is there a PTC fuse on the 5V rail?** (Search for F2 or similar)
4. **Do button/limit inputs have pull-up resistors?** (Search for R10-R20 range)
5. **Is the voltage divider for spindle correct?** (R7=10kΩ, R8=20kΩ?)

**To answer these questions:** Search the schematic systematically using KiCad's component search or text search in `hat.kicad_sch`.

---

**GOOD LUCK! 🚀**

This HAT is very close to being production-ready. The issues are fixable in 4-5 hours of focused work.
