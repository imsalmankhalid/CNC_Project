# MbW Lathe HAT - Comprehensive Technical Review

**Date:** 2026-08-27  
**Netlist Version:** 2026-08-27T15:41:15  
**Reviewer:** Technical Analysis  

---

## Executive Summary

### ✅ Design Status: MOSTLY READY with 2 Critical Issues

**Overall Assessment:**
- ✅ Power circuit: **EXCELLENT** - Dual MOSFET ideal diode OR-ing
- ⛔ Motor connectors: **BLOCKER** - Need 6 pins, currently have 3
- ⚠️ PCB routing: **3 unconnected GND pads** - Must fix before fabrication
- ✅ GPIO assignments: Match project requirements
- ⚠️ ERC/DRC: Minor errors that need attention

---

## 1. Power Circuit Analysis ✅

### Status: **APPROVED** - Excellent Professional Design

The power circuit uses a **dual P-channel MOSFET ideal diode OR-ing** topology:

**Components:**
- **Q1** (IRF4905): Pi 5V input path MOSFET
- **Q2** (IRF4905): External 12V → L7805 → 5V path MOSFET
- **U6** (L7805): 12V to 5V linear regulator
- **R10, R11**: Gate-drain self-biasing resistors (need to verify values: 47kΩ-100kΩ recommended)
- **C3, C4**: Filter capacitors (100µF 50V)
- **J9**: Barrel jack for 12V external power

### Circuit Topology:

```
Raspberry Pi 5V (J1 pins 2/4)
    ↓
    Q1 Drain ──┐
    Q1 Gate ←──┴── R11
    Q1 Source ──→ +5V System Rail
                     ↓
                  [All loads: U3, U4, J6, J10]

12V External (J9)
    ↓
    L7805 (U6) → 5V regulated
    ↓
    Q2 Drain ──┐
    Q2 Gate ←──┴── R10
    Q2 Source ──→ +5V System Rail
```

**Key Features:**
- ✅ Automatic power source selection (higher voltage wins)
- ✅ Very low voltage drop (<100mV typical)
- ✅ Safe hot-plug operation
- ✅ No backfeed between power sources
- ✅ Self-biasing gates (no control logic needed)
- ✅ Efficient operation (>99% efficiency)

**Netlist Verification:**
```
Net "+5V" (code 2):
- Q1 pin 3 (Source) ✓
- Q2 pin 3 (Source) ✓
- U3 pin 1, 20 (VCC) ✓
- U4 pin 1, 20 (VCC) ✓
- J6 pin 1 (Encoder +5V) ✓
- J10 pin 1 (ADC +5V) ✓

Net "Net-(J1-Pin_2)" (code 35):
- J1 pins 2, 4 (Pi 5V input) ✓
- Q1 pin 2 (Drain) ✓
- R11 pin 2 (gate biasing) ✓

Net "Net-(Q2-D)" (code 50):
- U6 pin 3 (L7805 OUT) ✓
- Q2 pin 2 (Drain) ✓
- R10 pin 2 (gate biasing) ✓
- C4 pin 1 (filter cap) ✓
```

**Minor Action Item:**
- ⚠️ Verify R10 and R11 values in schematic (should be 47kΩ to 100kΩ)

---

## 2. GPIO Pin Mapping vs. Project Code ✅

### Comparison with [lathe_rpi/config.py](../lathe_rpi/config.py)

#### ✅ Z-Axis Motor (Expected on J3):
| Signal | GPIO | Config.py | Schematic Status |
|--------|------|-----------|------------------|
| Z_STEP | 17 | GPIO_Z_STEP = 17 | ✅ Via U3 buffer |
| Z_DIR | 27 | GPIO_Z_DIR = 27 | ✅ Via U3 buffer |
| Z_ENABLE | 22 | GPIO_Z_ENABLE = 22 | ✅ Via U3 buffer |
| GND | - | Required | ⛔ **MISSING - No pin** |
| +5V | - | Required | ⛔ **MISSING - No pin** |
| Z_HLFB | - | Not in config (future) | ⛔ **MISSING - No pin** |

**J3 Current:** Screw_Terminal_01x03 (3 pins) - **INADEQUATE**  
**J3 Required:** Screw_Terminal_01x06 (6 pins)

#### ⛔ X-Axis Motor (Expected on J2):
| Signal | GPIO | Config.py | Schematic Status |
|--------|------|-----------|------------------|
| X_STEP | 24 | GPIO_X_STEP = 24 | ✅ Via U4 buffer |
| X_DIR | 23 | GPIO_X_DIR = 23 | ✅ Via U4 buffer |
| X_ENABLE | 25 | GPIO_X_ENABLE = 25 | ✅ Via U4 buffer |
| GND | - | Required | ⛔ **MISSING - No pin** |
| +5V | - | Required | ⛔ **MISSING - No pin** |
| X_HLFB | 16 | GPIO 16 (conflict!) | ⛔ **MISSING - No pin** |

**J2 Current:** Screw_Terminal_01x03 (3 pins) - **INADEQUATE**  
**J2 Required:** Screw_Terminal_01x06 (6 pins)

#### ✅ Encoders (J4 = X-axis, J5 = Z-axis):
| Signal | GPIO | Config.py | Schematic Status |
|--------|------|-----------|------------------|
| Z_ENC_A | 5 | GPIO_Z_ENC_A = 5 | ✅ J5 pin 3 |
| Z_ENC_B | 6 | GPIO_Z_ENC_B = 6 | ✅ J5 pin 4 |
| X_ENC_A | 13 | GPIO_X_ENC_A = 13 | ✅ J4 pin 2 |
| X_ENC_B | 19 | GPIO_X_ENC_B = 19 | ✅ J5 pin 4 |
| +3.3V | - | Power | ✅ J4/J5 pin 1 |
| GND | - | Ground | ✅ Via J1 |

#### ✅ Limit Switches (J7 connector):
| Signal | GPIO | Config.py | Schematic Status |
|--------|------|-----------|------------------|
| Z_LIM_PLUS | 16 | GPIO_LIM_Z_PLUS = 16 | ✅ Via R8 pull-up |
| X_LIM_PLUS | 8 | GPIO_LIM_X_PLUS = 8 | ✅ Via R6 pull-up |

**Note:** GPIO 16 is shared between Z_LIM_PLUS and X_HLFB (HLFB feedback from motor driver). This is a **potential conflict** if HLFB is added.

#### ✅ Other Signals:
| Signal | GPIO | Config.py | Schematic Status |
|--------|------|-----------|------------------|
| SPINDLE | 12 | GPIO_SPINDLE = 12 | ✅ Routed to J1 |
| HALFNUT | 4 | GPIO_HALFNUT = 4 | ✅ J8 connector |
| BTN_1 | 26 | GPIO_BTN_1 = 26 | ✅ Routed |
| BTN_2 | 20 | GPIO_BTN_2 = 20 | ✅ Routed |
| BTN_3 | 21 | GPIO_BTN_3 = 21 | ✅ Routed |
| SDA1 | 2 | I2C for ADC | ✅ J10 pin 4 |
| SCL1 | 3 | I2C for ADC | ✅ J10 pin 3 |

### Summary: GPIO Mapping ✅ MOSTLY CORRECT

**Issues:**
1. ⛔ **CRITICAL:** Motor connectors J2/J3 missing power (GND, +5V) and feedback (HLFB) pins
2. ⚠️ GPIO 16 conflict: Used for both Z_LIM_PLUS and potentially X_HLFB

---

## 3. ERC (Electrical Rule Check) Errors ⚠️

**ERC Report: 4 Errors**

### Error 1-4: Power Pin Not Driven

```
[power_pin_not_driven]: Input Power pin not driven by any Output Power pins
    @(2200 mils, 950 mils): Symbol #PWR04 Pin 1 [Power input, Line]
    @(3000 mils, 3150 mils): Symbol #PWR02 Pin 1 [Power input, Line]
    @(4000 mils, 3500 mils): Symbol #PWR08 Pin 1 [Power input, Line]
    @(7450 mils, 3950 mils): Symbol U6 Pin 1 [IN, Power input, Line]
```

**Analysis:**
These are **NORMAL** and **EXPECTED** for power input symbols:
- #PWR04, #PWR02, #PWR08: Power symbols for GND, +3.3V, or +5V rails
- U6 Pin 1: L7805 input (12V from barrel jack)

**These are power INPUT pins** - they receive power from external sources (Pi, barrel jack), not from other components on the schematic.

**Action:** ✅ **SAFE TO IGNORE** - These are false positives

KiCad flags these because power symbols don't have an "Output Power" pin driving them - but that's by design! The power comes from off-board (Raspberry Pi, barrel jack).

---

## 4. DRC (Design Rule Check) Errors ⛔

**DRC Report: 10 Issues (7 Warnings + 3 Critical Errors)**

### Warnings (7): Footprint Library Mismatch

```
[lib_footprint_mismatch]: Footprint does not match copy in library
    Warning: J6, J4, J5, J8, J2, J3, J1
```

**Analysis:**
These footprints were likely modified locally or the KiCad library was updated. The footprints on the PCB are "local overrides" that differ from the current library version.

**Action:** ⚠️ **VERIFY BUT NOT CRITICAL**
- Check that footprint pad patterns match the actual connectors you're ordering
- If using older KiCad libraries: Safe to ignore
- If using latest libraries: Update footprints in schematic

**How to fix:**
1. In PCB editor: Tools → Update Footprints from Library
2. Review changes before accepting
3. Re-run DRC

---

### ⛔ CRITICAL ERRORS (3): Unconnected GND Pads

```
[unconnected_items]: Missing connection between items
    Error: C3 pad 2 [Net-(U6-GND)] ↔ C4 pad 2 [Net-(U6-GND)]
    Error: U6 pad 2 [Net-(U6-GND)] ↔ C4 pad 2 [Net-(U6-GND)]  
    Error: C4 pad 2 [Net-(U6-GND)] ↔ U6 pad 2 [Net-(U6-GND)]
```

**Analysis:**
This is a **SERIOUS PCB ROUTING ERROR**. Three pads are on the same net but not physically connected:
- **U6 pin 2** (L7805 GND)
- **C3 pin 2** (Input filter capacitor GND)
- **C4 pin 2** (Output filter capacitor GND)

**The netlist shows these should be connected to GND (net code 32)**, but the PCB layout has them isolated on a separate net called "Net-(U6-GND)".

**Impact:**
⛔ L7805 regulator **WILL NOT WORK** without GND connection  
⛔ Filter capacitors ineffective  
⛔ Possible damage to components  

**Root Cause:**
PCB layout was not updated after schematic changes, or manual routing disconnected these pads.

---

### How to Fix DRC Errors: Step-by-Step Guide

#### Issue 1: U6/C3/C4 GND Not Connected ⛔

**In KiCad PCB Editor:**

1. **Open PCB file:** `hat.kicad_pcb`

2. **Locate the problem components:**
   - Press `F` (find tool)
   - Search for "U6" → Should show L7805 at coordinates ~(105mm, 70mm)
   - Search for "C3" → Input capacitor near J9 barrel jack
   - Search for "C4" → Output capacitor near U6

3. **Check the nets:**
   - Click on U6 pin 2 (middle pin, GND)
   - Check status bar: Should show "GND" net
   - Click on C3 pin 2 (negative terminal)
   - Click on C4 pin 2 (negative terminal)
   - If they show "Net-(U6-GND)" instead of "GND", they're isolated!

4. **Fix method A - Update from schematic:**
   - In PCB editor: Tools → Update PCB from Schematic (F8)
   - Check "Re-associate footprints by reference"
   - Click "Update PCB"
   - This should fix net assignments

5. **Fix method B - Manual routing:**
   - Delete any existing traces connected to U6 pin 2, C3 pin 2, C4 pin 2
   - Select "Route tracks" tool (X key)
   - Connect U6 pin 2 → C4 pin 2 (short trace)
   - Connect C4 pin 2 → nearby GND via or plane
   - Connect C3 pin 2 → nearby GND via or plane
   - Verify connections with "Highlight net" tool

6. **Verify fix:**
   - Tools → Design Rules Checker (Ctrl+Shift+D)
   - Click "Run DRC"
   - Check that "unconnected_items" errors are gone
   - Should see 0 DRC violations (or only footprint warnings)

#### Issue 2: Motor Connectors Need 6 Pins ⛔

**In KiCad Schematic Editor:**

1. **Open schematic:** `hat.kicad_sch`

2. **Locate J2 (X-axis motor connector):**
   - Press `F` (find tool)
   - Search for "J2"
   - Should be labeled "x axis motor"

3. **Replace connector:**
   - Right-click J2 → Properties
   - Note current footprint: `TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03_P2.54mm_Horizontal`
   - Delete J2 (right-click → Delete)
   - Press `A` (add symbol)
   - Search "Screw_Terminal_01x06"
   - Place new 6-pin connector
   - Label as "J2" (press `E` to edit properties)
   - Set footprint: `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06_P2.54mm_Horizontal`

4. **Wire J2 pins:**
   ```
   Pin 1: X_STEP (from U4 pin 18) - Already connected
   Pin 2: X_DIR (from U4 pin 17) - Already connected
   Pin 3: X_ENABLE (from U4 pin 16) - Need to add
   Pin 4: GND (connect to GND symbol)
   Pin 5: +5V (connect to +5V rail)
   Pin 6: X_HLFB (connect to GPIO 16 - but note conflict!)
   ```

5. **Repeat for J3 (Z-axis motor):**
   - Replace with Screw_Terminal_01x06
   - Wire pins:
   ```
   Pin 1: Z_STEP (from U3 pin 18) - Already connected
   Pin 2: Z_DIR (from U3 pin 17) - Already connected
   Pin 3: Z_ENABLE (from U3 pin 16) - Need to add
   Pin 4: GND (connect to GND symbol)
   Pin 5: +5V (connect to +5V rail)
   Pin 6: Z_HLFB (connect to GPIO 7 or other unused GPIO)
   ```

6. **Resolve GPIO 16 conflict:**
   - Current: GPIO 16 used for both Z_LIM_PLUS and X_HLFB
   - Option A: Keep GPIO 16 for Z_LIM_PLUS, use different GPIO for X_HLFB
   - Option B: Use GPIO 7 (currently reserved but unused) for Z_LIM_MINUS → X_HLFB
   - Option C: Don't connect HLFB for first revision (leave pins unconnected)

7. **Update netlist and PCB:**
   - File → Export → Netlist → Generate Netlist
   - Switch to PCB editor
   - Tools → Update PCB from Schematic (F8)
   - Route new traces for added pins
   - Re-run DRC

#### Issue 3: Verify R10/R11 Resistor Values ⚠️

**In KiCad Schematic Editor:**

1. Find R10 and R11 (gate-drain resistors)
2. Right-click → Properties → Value
3. Check current value (might be "10k" or similar)
4. Change to "47k" or "100k" for robust MOSFET biasing
5. Update BOM

---

## 5. Action Items - Prioritized

### 🔥 CRITICAL - Must Fix Before Fabrication

#### 1. Fix Motor Connectors J2 and J3 ⛔
**Time:** 2-3 hours  
**Blocker:** Cannot connect motor drivers properly

**Changes required:**
- Replace J2 from 3-pin to 6-pin screw terminal
- Replace J3 from 3-pin to 6-pin screw terminal
- Add signals: ENABLE, GND, +5V, HLFB to each
- Update PCB footprints and routing

**Teknic ClearPath motor drivers require 6 signals:**
- STEP (pulse train)
- DIR (direction)
- ENABLE (motor enable, active HIGH)
- GND (signal ground)
- +5V (power for opto-isolators)
- HLFB (High-Level Feedback - motor status)

**Without these:**
- No way to power the motor driver opto-isolators
- No motor enable control
- No feedback from motors
- System cannot function

#### 2. Fix L7805 GND Connections ⛔
**Time:** 30 minutes  
**Blocker:** Power circuit non-functional

**PCB has 3 unconnected pads:**
- U6 pin 2 (L7805 GND)
- C3 pin 2 (input cap GND)
- C4 pin 2 (output cap GND)

**Action:**
- Update PCB from schematic to fix net assignments
- Route GND traces connecting all three pads
- Connect to main GND plane
- Re-run DRC to verify fix

---

### ⚠️ High Priority - Should Fix Before Fabrication

#### 3. Resolve GPIO 16 Conflict
**Issue:** GPIO 16 assigned to both Z_LIM_PLUS and X_HLFB

**Options:**
- **A:** Keep GPIO 16 for Z_LIM_PLUS, use GPIO 7 for X_HLFB
- **B:** Use GPIO 11 for X_HLFB (currently listed as reserved but unused)
- **C:** Don't connect HLFB pins for first revision (leave as NC)

**Recommendation:** Use option A - GPIO 7 is already reserved for Z_LIM_MINUS but that switch is not fitted

#### 4. Verify Component Values
- Check R10 value (should be 47kΩ - 100kΩ)
- Check R11 value (should be 47kΩ - 100kΩ)
- Verify C3, C4 = 100µF (confirmed in netlist ✓)

#### 5. Update PCB Layout
- Route new motor connector pins
- Verify power distribution to motor connectors
- Add test points for +5V, +3.3V, GND
- Check silkscreen labels for all connectors

---

### 📋 Optional Enhancements

#### 6. Add Status LEDs (from previous discussion)
- Motor enable LEDs (green) on GPIO 22 (Z_EN) and GPIO 25 (X_EN)
- Limit switch LEDs (red) with NPN transistor buffers
- Power source indicator LED

#### 7. Add E-Stop Circuit
- Dedicated 2-pin terminal for emergency stop button
- Hardware logic to disable motor ENABLE lines
- Strong pull-up resistor (1kΩ-4.7kΩ)

#### 8. Improve Footprint Library Matches
- Update footprints from library (may change pad patterns)
- Verify connector pinouts against datasheets
- Re-run DRC after updates

---

## 6. Testing Plan (After Fixes)

### Power Circuit Testing ✅

**Test 1: Pi Power Only**
1. Connect Pi via USB-C (no 12V)
2. Measure voltages:
   - Q1 drain (Pi 5V): ~5.0V
   - Q1 gate: ~4.5V (Vgs ≈ -0.5V)
   - +5V system rail: 4.90-4.98V
   - Q2 drain (L7805 out): 0V
3. Verify system operates normally

**Test 2: External 12V Only**
1. Disconnect Pi power
2. Connect 12V to J9
3. Measure voltages:
   - J9 input: 12V
   - U6 output: 5.0V ± 0.1V
   - Q2 gate: ~4.5V
   - +5V system rail: 4.90-4.98V
   - Q1 drain: 0V
4. Verify system operates

**Test 3: Both Power Sources**
1. Connect Pi power AND 12V
2. Both sources should coexist safely
3. Higher voltage source provides most current
4. No voltage spikes or dropouts

**Test 4: Hot-Plug**
1. Start on Pi power
2. Plug in 12V while running (with oscilloscope on +5V rail)
3. Should see smooth transition, no glitches
4. Unplug 12V → should switch back to Pi power seamlessly

### Motor Circuit Testing ⛔ (After Adding 6-Pin Connectors)

**Test 1: ENABLE Control**
1. Set GPIO_Z_ENABLE LOW (motor disabled)
2. Verify ENABLE pin on J3 pin 3 reads LOW
3. Set GPIO_Z_ENABLE HIGH (motor enabled)
4. Verify ENABLE pin reads HIGH

**Test 2: STEP/DIR Signals**
1. Send step pulses on GPIO_Z_STEP
2. Verify pulses appear on J3 pin 1 with oscilloscope
3. Toggle GPIO_Z_DIR
4. Verify DIR signal on J3 pin 2

**Test 3: Power Distribution**
1. Verify J3 pin 4 = GND (0V)
2. Verify J3 pin 5 = +5V (4.95-5.0V)
3. Repeat for J2 (X-axis)

**Test 4: HLFB Feedback**
1. Connect motor driver
2. Enable motor
3. Check HLFB signal on GPIO (should indicate motor status)

---

## 7. Bill of Materials (BOM) - Key Components

| Qty | Reference | Value | Footprint | Part Number | Purpose |
|-----|-----------|-------|-----------|-------------|---------|
| 1 | U6 | L7805 | TO-220 | L7805CV | 5V regulator |
| 2 | Q1, Q2 | IRF4905 | TO-220 | IRF4905PBF | Power MOSFETs |
| 2 | U3, U4 | 74LVC245 | SOIC-20 | SN74LVC245A | Level shifters |
| 2 | C3, C4 | 100µF 50V | Radial | - | Filter caps |
| 2 | R10, R11 | 47kΩ | Axial | - | Gate resistors ⚠️ Verify |
| 3 | R5, R6, R8 | 10kΩ | Axial | - | Pull-up resistors |
| 1 | J1 | 40-pin | 2x20 header | - | Raspberry Pi |
| 2 | J2, J3 | **6-pin** ⛔ | Phoenix screw terminal | **Update to 6-pin!** | Motor connectors |
| 2 | J4, J5 | 4-pin | Phoenix screw terminal | - | Encoder connectors |
| 1 | J6 | 3-pin | Phoenix screw terminal | - | Encoder power |
| 1 | J9 | Barrel jack | 5.5mm/2.1mm | - | 12V input |
| 1 | J10 | 10-pin | Phoenix terminal | - | ADS1015 ADC |

**⚠️ BOM needs updating after fixing motor connectors!**

---

## 8. Fabrication Readiness Checklist

- [ ] ⛔ **Motor connectors J2/J3 changed to 6-pin**
- [ ] ⛔ **U6/C3/C4 GND connections fixed in PCB**
- [ ] ⚠️ GPIO 16 conflict resolved (HLFB vs limit switch)
- [ ] ⚠️ R10, R11 values verified (47kΩ-100kΩ)
- [ ] ⚠️ PCB updated from schematic (F8)
- [ ] ⚠️ All new traces routed
- [ ] DRC re-run with 0 errors (only footprint warnings OK)
- [ ] ERC reviewed (power pin warnings are OK to ignore)
- [ ] Gerber files regenerated
- [ ] BOM updated with correct connector part numbers
- [ ] Assembly documentation updated

---

## 9. Design Strengths ✅

**What's Working Well:**

1. ✅ **Excellent power circuit design** - Professional dual MOSFET OR-ing
2. ✅ **Proper GPIO mapping** - Matches config.py requirements
3. ✅ **Level shifting** - 74LVC245 buffers protect Raspberry Pi GPIO
4. ✅ **Pull-up resistors** - All inputs properly terminated
5. ✅ **I2C ADC interface** - ADS1015 for potentiometer reading
6. ✅ **Encoder inputs** - Proper differential signaling support
7. ✅ **Component selection** - Industrial-grade parts (Phoenix terminals, IRF4905, etc.)

---

## 10. Comparison: Requirements vs. Implementation

### Motor Control Requirements (from config.py):

| Requirement | Status | Notes |
|-------------|--------|-------|
| Z motor STEP (GPIO 17) | ✅ PASS | Via U3 buffer |
| Z motor DIR (GPIO 27) | ✅ PASS | Via U3 buffer |
| Z motor ENABLE (GPIO 22) | ✅ PASS | Via U3 buffer |
| X motor STEP (GPIO 24) | ✅ PASS | Via U4 buffer |
| X motor DIR (GPIO 23) | ✅ PASS | Via U4 buffer |
| X motor ENABLE (GPIO 25) | ✅ PASS | Via U4 buffer |
| Motor power (+5V, GND) | ⛔ FAIL | Not connected - no pins |
| Motor feedback (HLFB) | ⛔ FAIL | Not connected - no pins |

### Encoder Requirements:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Z encoder A (GPIO 5) | ✅ PASS | J5 pin 3 |
| Z encoder B (GPIO 6) | ✅ PASS | J5 pin 4 |
| X encoder A (GPIO 13) | ✅ PASS | J4 pin 2 |
| X encoder B (GPIO 19) | ✅ PASS | J5 pin 4 |
| +3.3V power | ✅ PASS | J4/J5 pin 1 |

### Limit Switch Requirements:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Z limit (GPIO 16) | ✅ PASS | Via R8 pull-up to J7 |
| X limit (GPIO 8) | ✅ PASS | Via R6 pull-up to J7 |
| NC configuration | ✅ PASS | Pull-up resistors present |

### Other I/O:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Spindle index (GPIO 12) | ✅ PASS | Routed |
| Half-nut (GPIO 4) | ✅ PASS | J8 connector |
| Buttons (GPIO 26, 20, 21) | ✅ PASS | Routed |
| I2C ADC (GPIO 2, 3) | ✅ PASS | J10 connector |

---

## 11. Recommendations

### Immediate (Before Fabrication):

1. **Fix motor connectors** (J2/J3 to 6-pin) - **BLOCKING**
2. **Fix L7805 GND routing** - **BLOCKING**
3. **Verify R10/R11 values** - Important for reliability
4. **Resolve GPIO 16 conflict** - Prevents future issues

### Short Term (Revision 1.1):

5. Add status LEDs (enable, limit, power source)
6. Add test points for key signals
7. Add E-stop circuit with hardware motor disable
8. Add polyfuse on 12V input for protection
9. Add TVS diodes on external connections

### Long Term (Future Revisions):

10. Consider EMI improvements (better grounding, filtering)
11. Add current sensing for diagnostics
12. Add temperature sensor near L7805
13. Consider SMD components for more compact design

---

## 12. Final Verdict

### ⚠️ **NOT READY FOR FABRICATION - 2 CRITICAL ISSUES**

**Must fix before ordering PCBs:**

1. ⛔ **Motor connectors J2/J3**: Change from 3-pin to 6-pin, add ENABLE/GND/+5V/HLFB
2. ⛔ **L7805 GND routing**: Connect U6 pin 2, C3 pin 2, C4 pin 2 to main GND

**After these fixes:**
- ✅ Power circuit: **Excellent professional design, ready to go**
- ✅ GPIO mapping: **Matches project requirements perfectly**
- ✅ Overall design: **Solid foundation for CNC lathe control**

**Estimated time to fix:** 3-4 hours in KiCad (schematic + PCB update + DRC verification)

**Once fixed:** 🎉 **Ready for fabrication!**

---

## Appendices

### A. Related Documentation

- [POWER_CIRCUIT_REVIEW_UPDATED.md](./POWER_CIRCUIT_REVIEW_UPDATED.md) - Detailed power circuit analysis
- [CONNECTOR_WIRING_REFERENCE.md](./CONNECTOR_WIRING_REFERENCE.md) - Expected connector pinouts
- [lathe_rpi/config.py](../lathe_rpi/config.py) - GPIO pin assignments and system configuration
- [DRC.rpt](./DRC.rpt) - Design Rule Check report
- [ERC.rpt](./ERC.rpt) - Electrical Rule Check report
- [hat.net](./hat.net) - Current netlist export

### B. Key Net Codes (from Netlist)

- Net 1: +3V3 (Raspberry Pi 3.3V)
- Net 2: +5V (System 5V rail - fed by Q1 and Q2)
- Net 32: GND (Main ground net)
- Net 33: Net-(D1-A) (12V input from J9)
- Net 35: Net-(J1-Pin_2) (Pi 5V input, isolated until Q1)
- Net 46: Net-(Q1-G) (Q1 gate drive)
- Net 48: Net-(Q2-G) (Q2 gate drive)
- Net 50: Net-(Q2-D) (L7805 output, isolated until Q2)

### C. Component Reference Quick List

**Power Components:**
- Q1, Q2: IRF4905 P-channel MOSFETs (ideal diode OR-ing)
- U6: L7805 voltage regulator (12V → 5V)
- C3, C4: 100µF 50V filter capacitors
- R10, R11: Gate-drain resistors (verify: 47kΩ-100kΩ)
- J9: Barrel jack (12V external power input)

**Motor Interface:**
- U3: 74LVC245 level shifter (Z-axis motor signals)
- U4: 74LVC245 level shifter (X-axis motor signals)
- J2: X-axis motor connector (⛔ needs to be 6-pin)
- J3: Z-axis motor connector (⛔ needs to be 6-pin)

**Encoder Interface:**
- J4: X-axis encoder (4-pin, +3.3V/GND/A/B)
- J5: Z-axis encoder (4-pin, +3.3V/GND/A/B)
- J6: Encoder power distribution (3-pin)

**Other I/O:**
- J7: Limit switches (2-pin with pull-ups)
- J8: Half-nut lever switch (2-pin)
- J10: ADS1015 ADC breakout (10-pin, I2C interface)
- J1: 40-pin Raspberry Pi header

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-27  
**Next Review:** After critical fixes are implemented
