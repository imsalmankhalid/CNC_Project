# DRC Error Analysis and Resolution Guide
**Date:** 2026-08-11  
**PCB Design:** MbW Lathe Control HAT  
**KiCad Version:** 10.0.4  
**Total Errors:** 16

---

## Executive Summary

The Design Rule Check (DRC) identified 16 violations in two categories:
1. **Track Width Violations** (12 errors) - Tracks below minimum width of 0.2mm
2. **Silkscreen Overlap Violations** (4 errors) - Component labels overlapping silkscreen graphics

All errors are fixable and do not represent fundamental design flaws. The track width issues require routing adjustments, while silkscreen issues are cosmetic and easily resolved by repositioning reference designators.

---

## Error Category 1: Track Width Violations

### Error Description
**Violation Type:** `track_width`  
**Board Constraint:** Minimum track width = 0.2000 mm  
**Actual Width:** 0.1500 mm  
**Severity:** ERROR  
**Count:** 12 violations

### Affected Signals and Locations

#### 1. I2C Signal - SDA1 (GPIO2)
**Critical - Data Line**

- **Track 1:** 0.07mm length at position (113.1005, 56.4505)
  - UUID: `45552b8e-4086-444c-bbc4-5b1b558e974c`
- **Track 2:** 2.06mm length at position (111.0386, 56.4505)
  - UUID: `ee0d4cc1-b606-464a-bbc3-83b25b17b885`

**Impact:** I2C communication line - sub-minimum width could cause signal integrity issues or manufacturing defects.

**Resolution:**
1. Widen tracks to **0.25mm minimum** (0.3mm recommended for I2C signals)
2. Ensure consistent width along entire SDA1 trace
3. Verify adequate clearance to adjacent traces
4. Consider adding pull-up resistor locations if not already present

---

#### 2. Connector Signal - Net-(J6-Pin_2)
**Moderate Priority**

- **Track 1:** 0.07mm length at position (108.8005, 57.5495)
  - UUID: `f0559f5e-2e21-4218-a132-e90d5db39c09`
- **Track 2:** 0.83mm length at position (107.9706, 57.5495)
  - UUID: `908b8dfe-211d-44e9-8f17-0ffd4f50b8a1`

**Impact:** Connection to J6 Pin 2 - narrow trace could fail during fabrication or cause intermittent connections.

**Resolution:**
1. Widen to **0.25mm minimum**
2. Check J6 connector datasheet for current requirements
3. If this is a power or high-current signal, consider 0.5mm+ width

---

#### 3. Transistor Base - Net-(Q2A-B1)
**High Priority - Control Signal**

- **Track 1:** 0.49mm length at position (153.3758, 56.5508)
  - UUID: `9e95dfad-efea-42fa-9cf7-c45f0e3717b2`
- **Track 2:** 0.97mm length at position (152.4044, 56.5508)
  - UUID: `c8a06c74-2e94-4291-9a17-a98299f690a7`

**Impact:** Base connection to transistor Q2A - critical for switching operation.

**Resolution:**
1. Widen to **0.25mm minimum**
2. Transistor base signals typically safe at 0.25-0.3mm
3. Verify base current requirements don't exceed trace capacity

---

#### 4. Power Supply - +5V
**CRITICAL - Power Distribution**

- **Track 1:** 0.49mm length at position (156.3492, 56.2992)
  - UUID: `4a8b8471-13cd-4c5c-b7a0-cd89221458af`
- **Track 2:** 2.13mm length at position (158.4823, 56.2992)
  - UUID: `77b750e5-1b78-4770-92af-9cc6d121d43c`

**Impact:** Main 5V power distribution - undersized traces can cause voltage drop, heating, and potential failure.

**Resolution:**
1. **Immediate Action Required:** Widen to minimum **0.8mm** for power distribution
2. Calculate actual current requirements for all 5V loads
3. Use trace width calculator: For 1A @ 5V, recommend 1.0mm width minimum
4. Consider using polygon pour for power distribution instead of traces
5. Add multiple vias if using planes on both layers

**Current Carrying Capacity Reference:**
- 0.15mm @ 1oz copper ≈ 0.3A (10°C rise)
- 0.80mm @ 1oz copper ≈ 1.5A (10°C rise)
- 1.00mm @ 1oz copper ≈ 2.0A (10°C rise)

---

#### 5. Transistor Gate - Net-(Q1-G)
**High Priority - MOSFET/Transistor Control**

- **Track 1:** 0.12mm length at position (160.5241, 57.2992)
  - UUID: `1edf8f8b-fbf2-4421-ac3d-b3499c65d171`
- **Track 2:** 1.44mm length at position (161.9617, 57.2992)
  - UUID: `96627878-2190-46f6-900e-862845e7ee02`
- **Track 3:** 0.71mm length at position (162.0261, 57.426)
  - UUID: `318e608a-9e5c-4c20-a888-5e8c25ecbe11`
- **Track 4:** 0.04mm length at position (162.0261, 57.3886)
  - UUID: `a5b2983d-61a7-40e7-b1e8-80611845d328`

**Impact:** Gate control signal for Q1 - affects switching characteristics and noise immunity.

**Resolution:**
1. Widen to **0.25mm minimum** (0.3mm recommended)
2. Gate signals benefit from wider traces for noise immunity
3. Keep trace short and direct to minimize parasitic inductance
4. Add gate resistor if not already present (typically 10-100Ω)

---

## Error Category 2: Silkscreen Overlap Violations

### Error Description
**Violation Type:** `silk_overlap`  
**Severity:** ERROR  
**Count:** 4 violations

These are **cosmetic issues** that affect manufacturing clarity but don't impact electrical function.

### Affected Components

#### 1. R7 and R8 Overlap
**Location:** (149.5, 83.19) and (148.08, 85.11)

- **Issue:** Reference label "R7" overlaps with R8's silkscreen rectangle
- **Resolution:**
  - Move R7 reference to top or left side of component
  - Alternative: Rotate reference 90° if space permits
  - Ensure 0.2mm minimum clearance between labels and graphics

---

#### 2. R7 and R5 Overlap
**Location:** (151.08, 85.11) and (152.5, 83.19)

- **Issue:** R7's silkscreen rectangle overlaps R5 reference label
- **Resolution:**
  - Move R5 reference to right side of component
  - Verify resistor orientation allows label repositioning
  - Consider hiding reference if space is extremely tight (mark on assembly drawing instead)

---

#### 3. R6 and R5 Overlap
**Location:** (155.5, 84.0) and (154.08, 85.11)

- **Issue:** R6 reference overlaps R5 silkscreen rectangle
- **Resolution:**
  - Move R6 reference above or to the right
  - Ensure minimum 0.2mm clearance
  - Check if resistors can be spaced slightly further apart

---

#### 4. C4 and C3 Overlap
**Location:** (104.15, 79.475) and (103.99, 80.186252)

- **Issue:** C4 reference overlaps C3 silkscreen segment
- **Resolution:**
  - Move C4 reference to opposite side of capacitor
  - Consider rotating reference 90° if horizontal space limited
  - Verify polarity markings remain clear after repositioning

---

## Recommended Action Plan

### Phase 1: Critical Issues (Do First)
**Priority: IMMEDIATE**

1. **Fix +5V Power Traces** ⚠️
   - Measure total current requirements for all 5V loads
   - Calculate required trace width (target 1.0mm minimum)
   - Re-route all +5V traces with adequate width
   - Consider copper polygon pour for power distribution
   - **Estimated Time:** 2-3 hours

### Phase 2: Signal Integrity Issues
**Priority: HIGH**

2. **Fix I2C Signal (SDA1)**
   - Widen to 0.3mm throughout
   - Verify SCL trace width matches
   - Check pull-up resistor values (typically 2.2kΩ - 4.7kΩ for 3.3V/5V)
   - **Estimated Time:** 30 minutes

3. **Fix Transistor Control Signals**
   - Widen Q1 gate and Q2A base traces to 0.25-0.3mm
   - Verify gate/base resistors are present
   - Check transistor datasheets for drive requirements
   - **Estimated Time:** 45 minutes

4. **Fix Connector Signal (J6-Pin_2)**
   - Determine signal type (power/signal/ground)
   - Widen appropriately (0.25mm min for signal, 0.5mm+ for power)
   - **Estimated Time:** 15 minutes

### Phase 3: Cosmetic Issues
**Priority: MEDIUM**

5. **Fix Silkscreen Overlaps**
   - Reposition all 4 overlapping reference designators
   - Verify manufacturing readability
   - Run DRC again to confirm resolution
   - **Estimated Time:** 30 minutes

### Phase 4: Verification
**Priority: HIGH**

6. **Complete Design Verification**
   - Run full DRC check
   - Verify all errors cleared
   - Check ERC (Electrical Rules Check) in schematic
   - Generate updated Gerber files
   - Review 3D model for mechanical clearances
   - **Estimated Time:** 1 hour

---

## Circuit Design Suggestions

### Power Distribution Improvements

1. **Use Polygon Pours for Power**
   - Convert +5V and GND traces to copper pours where possible
   - Reduces resistance and improves thermal performance
   - Easier to meet width requirements

2. **Add Decoupling Capacitors**
   - Verify 100nF ceramic caps near each IC power pin
   - Add 10µF electrolytic/tantalum at power input
   - Place as close as possible to IC pins

### Signal Integrity Improvements

3. **I2C Bus Conditioning**
   - Confirm pull-up resistor values appropriate for bus speed
   - Fast mode (400kHz): 2.2kΩ recommended
   - Standard mode (100kHz): 4.7kΩ typical
   - Consider series resistors (22-47Ω) for noise immunity

4. **Transistor Drive Circuits**
   - Add base/gate resistors if not present
   - Add gate-source/base-emitter resistors for defined off-state
   - Consider snubber circuits for inductive loads

### General Layout Improvements

5. **Ground Plane**
   - Implement solid ground plane on bottom layer if not already done
   - Minimize splits in ground plane
   - Use vias to connect ground pads to plane

6. **Thermal Management**
   - Check current-carrying components for adequate copper area
   - Add thermal reliefs where needed
   - Consider heavier copper (2oz) if budget allows

---

## Testing & Validation Checklist

After implementing fixes:

- [ ] All 12 track width violations cleared
- [ ] All 4 silkscreen violations cleared
- [ ] No new DRC errors introduced
- [ ] ERC check passes on schematic
- [ ] Power supply traces meet current requirements
- [ ] Critical signals (I2C, transistor controls) verified
- [ ] 3D view checked for mechanical issues
- [ ] Gerber files generated and reviewed
- [ ] BOM updated if components changed
- [ ] Assembly drawing updated with any position changes

---

## Technical Reference

### Trace Width Calculation Formula

**IPC-2221 Standard:**
```
I = k × ΔT^0.44 × A^0.725

Where:
I = Maximum current (Amps)
k = 0.048 for external layers, 0.024 for internal layers
ΔT = Temperature rise (°C)
A = Cross-sectional area (sq mils)
```

**Quick Reference (1oz copper, 10°C rise, external layer):**
| Width (mm) | Current (A) |
|------------|-------------|
| 0.15       | 0.3         |
| 0.25       | 0.5         |
| 0.50       | 1.0         |
| 0.80       | 1.5         |
| 1.00       | 2.0         |
| 1.50       | 2.7         |
| 2.00       | 3.5         |

### Minimum Clearances (Standard Manufacturing)

- **Track to Track:** 0.15mm minimum (0.20mm recommended)
- **Track to Pad:** 0.15mm minimum
- **Silkscreen to Copper:** 0.15mm minimum
- **Silkscreen to Silkscreen:** 0.15mm minimum
- **Via to Via:** 0.25mm recommended

---

## Files Modified

When implementing these fixes, the following file will be updated:
- `hat/hat.kicad_pcb` - Main PCB layout file

Related files to review:
- `hat/hat.kicad_sch` - Schematic (verify component values)
- `hat/DRC.json` - DRC results (will be regenerated)

---

## Conclusion

The identified DRC errors are all resolvable through layout adjustments. The most critical issue is the undersized +5V power traces, which could cause operational problems. Signal integrity issues with I2C and transistor control lines should also be addressed promptly.

Silkscreen overlaps are minor cosmetic issues that don't affect functionality but should be corrected for professional manufacturing.

**Estimated Total Time to Fix:** 5-6 hours  
**Risk Level After Fixes:** LOW  
**Recommended Review:** Have another engineer review power distribution calculations before ordering boards.

---

## Document History

| Date | Author | Changes |
|------|--------|---------|
| 2026-08-11 | GitHub Copilot | Initial analysis and resolution guide |

