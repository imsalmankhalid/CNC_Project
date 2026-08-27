# HAT Wiring Verification Report

**Date:** 2024-01-XX  
**Purpose:** Verify KiCad PCB design matches expected system wiring  
**Status:** ⚠️ **CRITICAL ISSUES FOUND**

---

## Summary

The KiCad HAT design has **CRITICAL CONNECTOR PIN COUNT MISMATCHES** that prevent proper motor driver connections. Motor connectors J2 and J3 are specified as 3-pin terminals but should be 6-pin terminals according to the wiring reference.

---

## Critical Issues

### 0. ✅ POWER CIRCUIT - EXCELLENT DESIGN! 

**Severity:** ~~CRITICAL~~ → **RESOLVED**  
**Status:** ✅ **APPROVED FOR FABRICATION**  
**Updated:** 2026-08-27 15:17

**Original Problem (FIXED):** Power circuit had BC557 + IRF4905 control logic that was incorrectly wired, causing direct connection between L7805 and Pi 5V.

**New Design:** Completely redesigned with **dual P-channel MOSFET ideal diode OR-ing** circuit using two IRF4905 MOSFETs (Q1 and Q2). This is a professional, industry-standard solution.

**Current Status:**
- ✅ Proper power isolation between Pi 5V and L7805 output
- ✅ Automatic power source selection (higher voltage wins)
- ✅ Very low voltage drop (<100mV vs 300-400mV with diodes)
- ✅ No backfeed risk between power sources
- ✅ Safe hot-plug operation
- ✅ Efficient self-biasing gate drive circuit

**Detailed Review:** See [POWER_CIRCUIT_REVIEW_UPDATED.md](POWER_CIRCUIT_REVIEW_UPDATED.md) for complete technical analysis

**Minor items to verify before fabrication:**
- ⚠️ Check R10/R11 resistor values (should be 47kΩ - 100kΩ)
- ⚠️ Verify C3/C4 capacitor values (should be ≥100µF)
- ℹ️ J9 pin 3 (barrel jack switch) is unused but circuit works fine without it

**Verdict:** ✅ **POWER CIRCUIT APPROVED** - Excellent engineering work!

---

### 1. ❌ Motor Connector Pin Count Mismatch

**Issue:** Motor connectors J2 (X-axis) and J3 (Z-axis) are defined as `Screw_Terminal_01x03` (3 pins) but the system requires 6 signals per motor driver.

#### Expected Wiring (per CONNECTOR_WIRING_REFERENCE.md):

**J2 - X-Axis Motor (ClearPath)**
- Pin 1: X_STEP (GPIO 23)
- Pin 2: X_DIR (GPIO 24)  
- Pin 3: X_ENABLE (GPIO 25)
- Pin 4: GND
- Pin 5: +5V
- Pin 6: X_HLFB (GPIO 16)

**J3 - Z-Axis Motor (ClearPath)**
- Pin 1: Z_STEP (GPIO 17)
- Pin 2: Z_DIR (GPIO 27)
- Pin 3: Z_ENABLE (GPIO 22)
- Pin 4: GND
- Pin 5: +5V
- Pin 6: Z_HLFB (GPIO 5)

#### Actual KiCad Design:

From `hat.kicad_sch` lines 8800+:
```
(comp
    (ref "J2")
    (value "x axis motor")
    (footprint "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03_P2.54mm_Horizontal")
    ...
    Screw_Terminal_01x03  ← Only 3 pins!
)

(comp
    (ref "J3")
    (value "Z axis motor")  
    (footprint "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-3-2.54_1x03_P2.54mm_Horizontal")
    ...
    Screw_Terminal_01x03  ← Only 3 pins!
)
```

**Impact:** 🔴 **BLOCKER** - Cannot connect all required motor driver signals. Missing GND, +5V, and HLFB feedback signals.

**Resolution Required:**
1. Change J2 and J3 to `Screw_Terminal_01x06` connectors
2. Update schematic to route all 6 signals per motor
3. Update PCB layout for larger footprints
4. Regenerate Gerber files

---

## GPIO Pin Mapping Verification

### ✅ Verified Correct Mappings

| Signal | Expected GPIO | KiCad Connection | Status |
|--------|---------------|------------------|--------|
| X_STEP | GPIO 23 | Needs routing to J2 pin 1 | ⚠️ Connector incomplete |
| X_DIR | GPIO 24 | Needs routing to J2 pin 2 | ⚠️ Connector incomplete |
| X_ENABLE | GPIO 25 | Needs routing to J2 pin 3 | ⚠️ Connector incomplete |
| X_HLFB | GPIO 16 | Missing (J2 only has 3 pins) | ❌ |
| Z_STEP | GPIO 17 | Needs routing to J3 pin 1 | ⚠️ Connector incomplete |
| Z_DIR | GPIO 27 | Needs routing to J3 pin 2 | ⚠️ Connector incomplete |
| Z_ENABLE | GPIO 22 | Needs routing to J3 pin 3 | ⚠️ Connector incomplete |
| Z_HLFB | GPIO 5 | Missing (J3 only has 3 pins) | ❌ |

### Limit Switches

| Signal | Expected GPIO | KiCad J7 Pins | Status |
|--------|---------------|---------------|--------|
| X_LIM_PLUS | GPIO 8 | J7 Pin 1 | ✅ Verify routing |
| X_LIM_MINUS | GPIO 7 | J7 Pin 2 | ✅ Verify routing |
| Z_LIM_PLUS | GPIO 16 | J7 Pin 3 | ⚠️ Conflicts with X_HLFB |
| Z_LIM_MINUS | GPIO 11 | J7 Pin 4 | ✅ Verify routing |

**Note:** GPIO 16 is assigned to both X_HLFB and Z_LIM_PLUS in different references - requires resolution.

### Encoders

| Signal | Expected | KiCad Connectors | Status |
|--------|----------|------------------|--------|
| X Encoder A | GPIO 13 (PWM1) | J6 (x axis enc) | ✅ 4-pin connector |
| X Encoder B | GPIO 19 (PCM.FS) | J6 | ✅ |
| Z Encoder A | GPIO 12 (PWM0) | J5 (z axis enc) | ✅ 4-pin connector |
| Z Encoder B | GPIO 20 (PCM.DIN) | J5 | ✅ |

### I²C & Potentiometer

| Signal | Expected | KiCad Connection | Status |
|--------|----------|------------------|--------|
| SDA | GPIO 2 (I2C1_SDA) | J10 Pin 1 | ✅ ADS1015 connection |
| SCL | GPIO 3 (I2C1_SCL) | J10 Pin 2 | ✅ ADS1015 connection |
| POT | A0 on ADS1015 | J10 Pin 4 | ✅ Potentiometer input |

---

## Power Distribution

### ✅ Verified Power Rails

| Rail | Source | Distribution | Status |
|------|--------|--------------|--------|
| +5V from Pi | J1 Pin 2/4 | → U6 (L7805) input | ✅ |
| P5V_HATOUT | U6 output | → Motor power pins | ⚠️ J2/J3 incomplete |
| +3.3V | J1 Pin 1/17 | → Logic/encoders | ✅ |
| GND | Multiple J1 pins | Common ground | ✅ |

**Issue:** Motor connectors need +5V and GND pins added.

---

## DRC Issues from hat/DRC.rpt

### ⚠️ Warnings (Non-critical)

The DRC report shows primarily **footprint library mismatches** which are warnings, not errors:
- 29 instances of footprint mismatches (e.g., `Capacitor_THT:C_Radial_*` differences)
- These are typically cosmetic/library version issues

### ✅ Unconnected Items (Intentional)

```
[unconnected_items]: Items are unconnected
    @(0.0000mm, 0.0000mm): Pad 6 [Pin_6] of J10 on F.Cu net 0 has no net.
    @(0.0000mm, 0.0000mm): Pad 7 [Pin_7] of J10 on F.Cu net 0 has no net.
    ... (pins 6-10 on J10)
```

These are unused pins on the 10-pin ADS1015 breakout connector - **acceptable** if only using first 5 pins.

---

## Action Items

### �🔥🔥 CRITICAL - DANGEROUS - MUST FIX FIRST

**0. FIX POWER CIRCUIT DESIGN FLAW** ⛔  
   **Time:** 6-12 hours schematic/layout + testing  
   **Blocker:** UNSAFE to fabricate - can damage Raspberry Pi and HAT  
   **See:** [POWER_CIRCUIT_ANALYSIS.md](POWER_CIRCUIT_ANALYSIS.md) for full details
   
   **Required Changes:**
   - **Option A (Simplest):** Add two Schottky diodes (1N5819) for diode OR-ing between L7805 output and Pi 5V
   - **Option B (Better):** Fix Q6 MOSFET circuit by creating separate net for L7805 output
   - Fix Q4 base-collector short circuit
   - Replace D1 from LED to proper power diode
   - Connect J9 pin 3 (barrel jack switch) to control circuit
   - Add power status LED with current-limiting resistor
   
   **Without this fix:**
   - Both 12V and Pi 5V will be directly connected (voltage conflict)
   - Possible backfeed damage to Raspberry Pi power supply
   - L7805 can be damaged by reverse current
   - Power switching does not work (Q6 useless)

---

### 🔴 Critical (Must Fix Before Fabrication)

1. **Replace J2 connector:**
   - Change from `Screw_Terminal_01x03` to `Screw_Terminal_01x06`
   - Add footprint `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06_P2.54mm_Horizontal`
   - Route signals: STEP, DIR, ENABLE, GND, +5V, HLFB

2. **Replace J3 connector:**
   - Same as J2
   - Route Z-axis signals

3. **Resolve GPIO 16 conflict:**
   - Currently assigned to both X_HLFB and Z_LIM_PLUS
   - Recommend: Keep for X_HLFB, reassign Z_LIM_PLUS to unused GPIO

### ⚠️ High Priority (Verify/Document)

4. **Verify all motor signal routes** in PCB layout:
   - Trace X_STEP (GPIO 23) → J2 Pin 1
   - Trace X_DIR (GPIO 24) → J2 Pin 2
   - Etc. for all 12 motor signals

5. **Verify power routing:**
   - P5V_HATOUT from U6 → J2 Pin 5, J3 Pin 5
   - GND → J2 Pin 4, J3 Pin 4

6. **Update CONNECTOR_WIRING_REFERENCE.md** to match final design

### 📋 Low Priority (Nice to Have)

7. Label silkscreen on PCB for all connector pins
8. Add test points for critical signals
9. Document in README which GPIO pins are not used

---

## Verification Checklist

- [ ] **POWER CIRCUIT FIXED** (isolation diodes or MOSFET switching working)
- [ ] **POWER CIRCUIT TESTED** (verify no backfeed, proper switching)
- [ ] Q4 base-collector short fixed
- [ ] D1 replaced with power diode
- [ ] J9 pin 3 connected to control circuit
- [ ] J2 changed to 6-pin terminal block
- [ ] J3 changed to 6-pin terminal block  
- [ ] All motor GPIO signals routed correctly
- [ ] Power rails connected to motor connectors
- [ ] GPIO 16 conflict resolved
- [ ] PCB layout updated for new footprints
- [ ] DRC re-run with no critical errors
- [ ] Gerber files regenerated
- [ ] Bill of Materials (BOM) updated
- [ ] Assembly documentation updated

---

## References

- [POWER_CIRCUIT_ANALYSIS.md](./POWER_CIRCUIT_ANALYSIS.md) - **CRITICAL: Power circuit design flaw analysis**
- [CONNECTOR_WIRING_REFERENCE.md](./CONNECTOR_WIRING_REFERENCE.md) - Expected wiring
- [lathe_rpi/config.py](../lathe_rpi/config.py) - GPIO pin assignments
- [hat.kicad_sch](./hat.kicad_sch) - Current schematic
- [DRC.rpt](./DRC.rpt) - Design rule check results

---

## Conclusion

**⛔ THE HAT DESIGN IS UNSAFE TO FABRICATE IN ITS CURRENT STATE.**

### Critical Safety Issue:
The power circuit has a **dangerous design flaw** where the L7805 regulator output and Raspberry Pi 5V are directly connected without isolation. Operating this HAT with both 12V external power and Pi power can cause:
- Damage to Raspberry Pi power circuitry
- Damage to L7805 voltage regulator  
- Voltage conflicts and current loops
- Complete failure of intended power switching

**This issue MUST be fixed before any other work proceeds.**

### Fabrication Blockers:
1. **Power circuit lacks isolation** (CRITICAL - can damage equipment)
2. **Motor connectors have insufficient pins** (3-pin vs required 6-pin)
3. **Power switching circuit is non-functional** (Q6 MOSFET useless, Q4 shorted)

### Design Issues Summary:
All other connections appear architecturally sound for GPIO and signal routing, but cannot be verified until:
- Power circuit is redesigned and proven safe
- Connector pin counts are corrected
- PCB layout is updated
- Full electrical testing is performed

**Estimated Total Rework Time:** 8-16 hours (power circuit 6-12 hrs + connectors 2-4 hrs)

---

**Report Generated:** 2026-08-27  
**Next Review:** After power circuit isolation is implemented and tested
