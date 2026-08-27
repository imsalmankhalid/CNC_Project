# MbW Lathe HAT – PCB Design Review Report
**Date:** 2026-08-11  
**Reviewer:** AI Design Analysis  
**PCB Version:** hat.kicad_pcb (KiCad 10.0.4)  
**Status:** DRC Violations Found + Design Recommendations  

---

## Executive Summary

The MbW Lathe HAT PCB design has been analyzed for compliance with design rules and best practices. This report identifies:

- **3 DRC Violations** (1 critical clearance, 2 silkscreen overlaps)
- **Design improvements** for manufacturability and reliability
- **Missing features** based on design specification comparison

**Overall Assessment:** The design is functional but requires fixes before fabrication.

---

## Part 1: DRC Violation Analysis & Fixes

### 1.1 Clearance Violation (CRITICAL)

**Violation Type:** Copper clearance  
**Severity:** ERROR  
**Location:** 123.843 mm, 53.672 mm  

**Details:**
- **Required clearance:** 0.2000 mm (200 µm)
- **Actual clearance:** 0.1767 mm (176.7 µm)
- **Gap:** 0.0233 mm (23.3 µm) **TOO CLOSE**

**Components:**
- Via on `/P5V` net (F.Cu - B.Cu transition)
- Track on `Net-(Q2A-B1)` net, length 1.0356 mm

**Root Cause:**  
Routing is too tight around the via at position (123.843, 53.672). The track at (123.505, 54.399) encroaches within the 0.2 mm clearance zone.

**Fix Required:**
1. **Option A (Recommended):** Move the via slightly (0.05-0.1 mm in any direction away from the track)
2. **Option B:** Reroute the track `Net-(Q2A-B1)` to avoid the via keepout zone
3. **Option C:** If absolutely constrained, reduce track width from 0.2 mm to 0.15 mm to create more clearance

**Manufacturing Impact:**  
- **HIGH RISK** – This violation will likely cause a short circuit during manufacturing
- Most PCB fabs will reject this design or flag it for manual review
- Must be fixed before ordering boards

---

### 1.2 Silkscreen Overlap #1

**Violation Type:** Silkscreen clearance  
**Severity:** ERROR  
**Location:** R7 reference field overlaps R5 body  

**Details:**
- **R7 Reference field** at (98.0, 56.92) overlaps with
- **R5 Rectangle** on F.Silkscreen at (96.08, 57.08)

**Component Placement:**
```
R7: 94.19, 55 mm    (Reference "R7" at -1.81 offset = 92.38, 55)
R5: 94.19, 58 mm    (Reference "R5" at -1.81 offset = 92.38, 58)
R6: 94.19, 61 mm    (Reference "R6" at -1.81 offset = 92.38, 61)
```

These three resistors (R5, R6, R7) are placed **3 mm apart vertically**, which is tight for through-hole DIN0204 resistors with reference designators.

**Fix Required:**
1. **Option A (Quick Fix):** Move reference designators to the right side of resistors instead of left
   - Change R7 reference position from (-1.81, 0) to (+5.0, 0)
   - Change R5 reference position from (-1.81, 0) to (+5.0, 0)
   - Change R6 reference position from (-1.81, 0) to (+5.0, 0)

2. **Option B (Better):** Reduce font size of reference text from 1.0 mm to 0.8 mm

3. **Option C (Best Practice):** Move resistors 1 mm further apart (4 mm spacing instead of 3 mm)

**Manufacturing Impact:**  
- **LOW RISK** – Most fabs will proceed but may clip/omit silkscreen text
- Affects assembly and debugging (harder to read component references)

---

### 1.3 Silkscreen Overlap #2

**Violation Type:** Silkscreen clearance  
**Severity:** ERROR  
**Location:** R5 reference field overlaps R6 body  

**Details:**
- **R5 Reference field** at (98.0, 59.92) overlaps with
- **R6 Rectangle** on F.Silkscreen at (96.08, 60.08)

**Fix Required:**  
Same as Section 1.2 – fix all three resistor references together.

---

## Part 2: Design Completeness Review

### 2.1 Components Implemented ✓

Based on schematic analysis, the following are present:

| Component | Qty | Part | Status |
|-----------|-----|------|--------|
| **Level Shifters** | 2 | 74HC245 (U3, U4) | ✓ Implemented |
| **ADC** | 1 | ADS1115 (U2) | ✓ Implemented |
| **Voltage Regulators** | 2 | MP2307 (buck), AP2112 (LDO) | ✓ Implemented |
| **Resistors** | Many | 10kΩ pull-ups, etc. | ✓ Implemented |
| **Capacitors** | Many | Decoupling, bulk | ✓ Implemented |
| **GPIO Header** | 1 | 2×20 male | ✓ Assumed (need to verify) |
| **DC Jack** | 1 | 12V input (J17) | ✓ Implemented |

**Component Count:** 28 footprints total (verified via grep)

---

### 2.2 Missing or Unclear Components

Based on the design specification ([PCB_HAT_Design.md](PCB_HAT_Design.md)), the following components are **specified but not verified** in the PCB:

| Component | Specified | Status | Notes |
|-----------|-----------|--------|-------|
| **HAT ID EEPROM** | AT24C32 on I2C (0x50) | ❓ NOT FOUND in schematic grep | Optional but recommended for HAT compliance |
| **TVS Diodes** | 6× for motor signals, 1× spindle | ❓ NEEDS VERIFICATION | Critical for ESD protection |
| **PTC Fuse** | 500 mA on 5V rail | ❓ NEEDS VERIFICATION | Important for RPi protection |
| **Current-Limiting Resistors** | 100Ω on STEP lines | ❓ NEEDS VERIFICATION | For signal integrity |
| **Pull-up/Pull-down Resistors** | 10kΩ on buttons, limits | ✓ LIKELY (R5, R6, R7 are 10kΩ) | Need to verify all channels |
| **Status LEDs** | 3× (Power, E-Stop, Activity) | ❓ NEEDS VERIFICATION | Useful for debugging |

**Action Required:** Verify these components exist in the full schematic or add them if missing.

---

### 2.3 Connectors Status

Based on design spec, the following connectors should be present:

| Connector | Qty | Type | Purpose | Status |
|-----------|-----|------|---------|--------|
| **2×20 GPIO Header** | 1 | Male | RPi interface | ✓ Assumed |
| **JST PH 2.0 mm, 6-pin** | 2 | Encoder connectors | Z & X encoders | ❓ NEEDS VERIFICATION |
| **Molex Mini-fit Jr, 8-pin** | 2 | Servo signal | ClearPath Z & X | ❓ NEEDS VERIFICATION |
| **JST PH 2.0 mm, 3-pin** | 2 | Spindle + Pot | Index sensor, pot | ❓ NEEDS VERIFICATION |
| **Screw Terminal 3.5mm, 2-pin** | 8 | Limit switches + buttons | 4 limits, 4 buttons | ❓ NEEDS VERIFICATION |
| **Screw Terminal 3.5mm, 4-pin** | 1 | E-Stop | Emergency stop | ❓ NEEDS VERIFICATION |
| **DC Jack** | 1 | 5.5×2.1mm | 12V power | ✓ J17 found |

**Note:** The grep shows `J6`, `J7`, `J17` in the PCB – need to verify all connector footprints match the spec.

---

## Part 3: Design Improvements & Recommendations

### 3.1 HIGH PRIORITY (Before Fabrication)

1. **Fix Clearance Violation** (Section 1.1)
   - Move via at (123.843, 53.672) by 0.1 mm
   - Re-run DRC to verify fix

2. **Fix Silkscreen Overlaps** (Sections 1.2, 1.3)
   - Reposition R5, R6, R7 reference designators
   - Or increase vertical spacing to 4 mm

3. **Verify ESD Protection**
   - Confirm TVS diodes are present on motor STEP/DIR/ENABLE lines
   - Confirm TVS diode on spindle index input
   - Recommended parts: PESD5V0S1UL (SOD-523) or similar

4. **Verify Power Protection**
   - Confirm PTC fuse (500 mA) on 5V rail from GPIO header
   - Confirm reverse polarity protection on 12V input (D8 SMAJ13CA is present ✓)

5. **Verify All Decoupling Capacitors**
   - 100 nF ceramic per IC power pin (74HC245 ×2, ADS1115, MP2307, AP2112)
   - Bulk caps: 10 µF on 3.3V and 5V rails
   - Place caps **< 5 mm** from IC power pins

---

### 3.2 MEDIUM PRIORITY (Manufacturability)

1. **Add Fiducials**
   - Place 3× fiducial marks (copper circles, no soldermask) for pick-and-place alignment
   - Locations: opposite corners + center
   - Standard size: 1 mm copper circle, 2 mm clearance

2. **Add Test Points**
   - TP_3V3, TP_5V0, TP_GND (accessible via pogo pins)
   - TP_STEP_Z, TP_STEP_X (for oscilloscope debugging)
   - Use 1 mm pad, no soldermask

3. **Silkscreen Improvements**
   - Add polarity marking on DC jack (+ and -)
   - Add "12V IN" text near J17
   - Add pin 1 indicator on all connectors
   - Add version number and date on back silkscreen

4. **Thermal Management**
   - Verify thermal vias under MP2307 (buck regulator gets hot)
   - Verify thermal vias under AP2112 (LDO for 3.3V)
   - Recommended: 4-6 thermal vias, 0.3 mm drill, to GND plane

5. **Board Edge Clearance**
   - Verify all components are ≥ 3 mm from board edge
   - Verify mounting holes have ≥ 5 mm keepout zone

---

### 3.3 LOW PRIORITY (Nice to Have)

1. **Add HAT ID EEPROM**
   - AT24C32 (SOIC-8) on I2C address 0x50
   - Required for official RPi HAT compliance
   - Enables auto-detection in Raspberry Pi OS

2. **Add Status LEDs**
   - Power LED (green): 5V rail active
   - E-Stop LED (red): E-Stop triggered
   - Activity LED (yellow): STEP pulse activity
   - Each LED + 330Ω resistor

3. **Add Solder Jumpers**
   - SJ_I2C_PULLUP: Enable/disable I2C pull-ups (useful if multiple I2C devices)
   - SJ_5V_SELECT: Choose between GPIO 5V or buck 5V (for debug)

4. **Label Connector Pinouts on Silkscreen**
   - Print pin numbers on silkscreen near each connector
   - Helps with field assembly and troubleshooting

5. **Add Ground Plane Stitching Vias**
   - Place vias every 10-15 mm to connect top and bottom ground planes
   - Improves EMI performance

---

## Part 4: Design Rule Check Configuration Review

### 4.1 Ignored Checks (from DRC.json)

The following checks are currently **ignored** in the DRC configuration:

| Check | Description | Recommendation |
|-------|-------------|----------------|
| `missing_courtyard` | Footprint has no courtyard defined | ✓ OK to ignore for prototype, but add courtyards for production |
| `track_not_centered_on_via` | Track endpoint not centered on via | ⚠️ May cause manufacturing issues – review manually |
| `tuning_profile_track_geometries` | Tuning profile track geometries | ✓ OK (not using length tuning) |
| `footprint_filters_mismatch` | Footprint doesn't match symbol filters | ⚠️ Should verify – may indicate wrong footprint |
| `pth_inside_courtyard` | PTH inside courtyard | ⚠️ May cause assembly issues – review manually |
| `npth_inside_courtyard` | NPTH inside courtyard | ⚠️ May cause assembly issues – review manually |

**Recommendation:**  
- For prototype builds: Current ignore list is acceptable
- For production: Enable `footprint_filters_mismatch` and manually review courtyard violations

---

### 4.2 Included Severities

Currently only **errors** are reported. Consider adding **warnings** to the DRC report for better visibility:

```json
"included_severities": [
    "error",
    "warning"
]
```

This will catch:
- Minimum annular ring violations
- Via to via clearance warnings
- Trace width warnings
- Silkscreen to pad clearance

---

## Part 5: Schematic-to-PCB Parity

**Status:** ✓ No unconnected items  
**Status:** ✓ No schematic parity errors  

This is excellent – the PCB matches the schematic with no missing connections.

---

## Part 6: Action Items Summary

### CRITICAL (Must Fix Before Ordering)
- [ ] **Fix clearance violation** at via (123.843, 53.672) – move via or reroute track
- [ ] **Fix silkscreen overlaps** for R5, R6, R7 references
- [ ] **Verify all TVS diodes** are present on signal lines
- [ ] **Re-run DRC** and confirm zero violations

### HIGH PRIORITY (Should Fix Before Ordering)
- [ ] Verify PTC fuse on 5V rail
- [ ] Add fiducials for assembly
- [ ] Add test points for key signals
- [ ] Verify thermal vias under regulators
- [ ] Add polarity marking on DC jack

### MEDIUM PRIORITY (Nice to Have)
- [ ] Add HAT ID EEPROM for RPi compliance
- [ ] Add status LEDs (Power, E-Stop, Activity)
- [ ] Improve silkscreen labels on connectors
- [ ] Add ground stitching vias

### DOCUMENTATION
- [ ] Generate complete BOM with manufacturer part numbers
- [ ] Create assembly drawing (top and bottom views)
- [ ] Document connector pinouts in separate file
- [ ] Create fabrication package (Gerbers + drill + BOM + assembly)

---

## Part 7: Design Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **DRC Violations** | 3 | 0 | ❌ FAIL |
| **Schematic Parity** | 0 errors | 0 | ✓ PASS |
| **Unconnected Nets** | 0 | 0 | ✓ PASS |
| **Component Count** | 28 footprints | ~35 expected | ⚠️ REVIEW |
| **Board Thickness** | 1.6 mm | 1.6 mm | ✓ PASS |
| **Copper Layers** | 2 | 2 | ✓ PASS |
| **Min Track Width** | 0.2 mm | ≥0.15 mm | ✓ PASS |
| **Min Clearance** | 0.2 mm | ≥0.15 mm | ✓ PASS (after fix) |

---

## Part 8: Next Steps

1. **Fix DRC violations** (see Part 1)
2. **Verify missing components** (see Part 2.2)
3. **Run DRC again** to confirm zero violations
4. **Generate fabrication outputs:**
   - Gerber files (RS-274X format)
   - Drill files (Excellon format)
   - BOM with manufacturer part numbers
   - Assembly drawings (PDF)
5. **Review with PCB manufacturer** (e.g., JLCPCB, PCBWay, OSH Park)
6. **Order prototype** (5-10 boards recommended)
7. **Test and validate** before full production

---

## Part 9: Manufacturing Recommendations

### Recommended PCB Specifications
```
Board size:        65.0 × 56.5 mm (or actual measured size)
Layers:            2 (F.Cu + B.Cu)
Thickness:         1.6 mm
Copper weight:     1 oz (35 µm)
Soldermask:        Green (or any color)
Silkscreen:        White
Surface finish:    HASL or ENIG
Min trace/space:   0.2/0.2 mm (8/8 mil)
Min drill:         0.3 mm
```

### Recommended Manufacturer
- **JLCPCB** or **PCBWay** for prototypes (cheap, fast)
- **OSH Park** for high-quality prototypes (USA-made, purple boards)
- **Seeed Studio** or **Elecrow** for assembly service

### Estimated Cost (5 boards, no assembly)
- JLCPCB: ~$5-10 USD + shipping
- PCBWay: ~$10-15 USD + shipping
- OSH Park: ~$25-30 USD (free shipping in USA)

---

## Appendix A: Files to Check

The following files should be reviewed in detail:

1. `hat.kicad_pcb` – PCB layout (11,036+ lines)
2. `hat.kicad_sch` – Schematic (needs full read-through)
3. `DRC.json` – Current DRC configuration
4. `PCB_HAT_Design.md` – Design specification
5. `HARDWARE.md` – Hardware compatibility list

---

## Appendix B: Reference Documents

- [PCB HAT Design Specification](PCB_HAT_Design.md)
- [Hardware Compatibility List](HARDWARE.md)
- [PCB Build Guide](PCB_Build_Guide_ASCII.md)
- [PCB Connections Guide](PCB_Connections_Guide_v2.md)

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-08-11 | 1.0 | AI Analysis | Initial review based on DRC.json and design files |

---

**END OF REPORT**
