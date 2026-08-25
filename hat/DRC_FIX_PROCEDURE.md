# Step-by-Step DRC Fix Procedure for KiCad

**File:** `hat.kicad_pcb`  
**Date:** 2026-08-11  
**Total Errors:** 16 (12 track width + 4 silkscreen overlap)

---

## ⚠️ Before You Start

1. **Backup your design:**
   ```bash
   cp hat.kicad_pcb hat.kicad_pcb.backup
   ```

2. **Open KiCad PCB Editor:**
   - Launch KiCad
   - Open Project: `hat.kicad_pro`
   - Open PCB Editor (Pcbnew)

---

## Part 1: Fixing Track Width Violations (12 errors)

### Method 1: Fix Individual Tracks Using DRC Markers

1. **Open DRC Window:**
   - Menu: `Inspect` → `Design Rules Checker`
   - Or press `Ctrl+Shift+I`

2. **For each track width violation:**
   - Double-click the error in the DRC list
   - KiCad will zoom to the problematic track
   - **Select the track** (click on it)
   - Press `E` to edit track properties
   - Change `Width` field to appropriate value:
     - **+5V tracks:** 1.0 mm (minimum 0.8mm)
     - **Signal tracks (I2C/GPIO):** 0.3 mm (minimum 0.25mm)
     - **Control signals (Gate/Base):** 0.25 mm
   - Press `OK`

3. **Fix connected segments:**
   - Some tracks have multiple segments
   - Select all segments of the same net
   - Right-click → `Select` → `Filter Selection`
   - Choose `Tracks` and same `Net`
   - Edit properties for all selected (Press `E`)

### Method 2: Global Track Width Update

1. **Edit Track & Via Sizes:**
   - Menu: `File` → `Board Setup`
   - Go to `Design Rules` → `Pre-defined Sizes`
   
2. **Set appropriate track widths:**
   - Add new track widths:
     ```
     0.25 mm  (signal traces)
     0.30 mm  (I2C, critical signals)
     0.50 mm  (moderate power)
     0.80 mm  (power traces)
     1.00 mm  (main power)
     ```

3. **Update existing tracks:**
   - Select tracks by net:
     - Press `Ctrl+F` (Find)
     - Enter net name (e.g., "+5V")
     - Right-click selected items
     - Choose `Change Track Width`
     - Select appropriate width from dropdown

### Specific Fixes by Net:

#### Fix 1: +5V Power Net (CRITICAL)
**Errors:** 2 violations  
**Current width:** 0.15mm  
**Required width:** 1.0mm minimum

**Steps:**
1. Press `Ctrl+F`, search for net `+5V`
2. Right-click → `Select` → `Items of Same Net`
3. Right-click → `Edit Track & Via Properties`
4. Set width to `1.0`
5. Click `OK`

#### Fix 2: I2C SDA1 Signal
**Errors:** 2 violations  
**Net:** `/GPIO2/SDA1` or `/GPIO2{slash}SDA1`  
**Current width:** 0.15mm  
**Required width:** 0.30mm

**Steps:**
1. Find and select SDA1 net tracks
2. Edit properties → Width: `0.30`
3. Also check SCL (Clock) line and match width

#### Fix 3: J6-Pin_2 Connector
**Errors:** 2 violations  
**Net:** `Net-(J6-Pin_2)`  
**Required width:** 0.25mm minimum

**Steps:**
1. Determine signal type at J6 Pin 2 from schematic
2. If power: use 0.5mm, if signal: use 0.25mm
3. Update track width accordingly

#### Fix 4: Transistor Q1 Gate
**Errors:** 4 violations  
**Net:** `Net-(Q1-G)`  
**Required width:** 0.25mm

**Steps:**
1. Select all Q1 gate tracks
2. Set width to `0.30` (extra margin for noise immunity)

#### Fix 5: Transistor Q2A Base  
**Errors:** 2 violations  
**Net:** `Net-(Q2A-B1)`  
**Required width:** 0.25mm

**Steps:**
1. Select all Q2A base tracks
2. Set width to `0.25`

---

## Part 2: Fixing Silkscreen Overlap Violations (4 errors)

### Method: Reposition Reference Designators

1. **Open DRC and locate silk overlap errors**

2. **For each silkscreen violation:**

#### Fix 1: R7 and R8 Overlap
**Location:** ~(149.5, 83.19)

**Steps:**
1. Click on resistor R7
2. Press `E` to edit
3. Click on the `Reference` field
4. Press `M` to move it
5. Place it **above** or **to the left** of R7 body
6. Ensure 0.2mm clearance from R8 silkscreen

#### Fix 2: R7 and R5 Overlap
**Location:** ~(151.08, 85.11)

**Steps:**
1. Move R5 reference to the **right** side
2. Or move R7's silkscreen away
3. Verify 0.2mm minimum clearance

#### Fix 3: R6 and R5 Overlap
**Location:** ~(155.5, 84.0)

**Steps:**
1. Move R6 reference **above** or **right**
2. Check clearance from all nearby silkscreen

#### Fix 4: C4 and C3 Overlap
**Location:** ~(104.15, 79.475)

**Steps:**
1. Move C4 reference to opposite side of capacitor
2. Alternative: Rotate reference 90° if needed
3. Ensure polarity markings remain visible

---

## Part 3: Verification

1. **Run DRC Again:**
   - Press `Ctrl+Shift+I`
   - Click `Run DRC`
   - Verify all errors cleared
   - Check for any new violations introduced

2. **Visual Inspection:**
   - Press `Alt+3` for 3D Viewer
   - Check component clearances
   - Verify silkscreen legibility

3. **Check Design Rules:**
   - Menu: `File` → `Board Setup` → `Design Rules` → `Constraints`
   - Verify:
     ```
     Minimum track width: 0.2 mm
     Minimum clearance: 0.15 mm
     Minimum annular width: 0.13 mm
     ```

4. **Electrical Rules Check:**
   - Switch to Schematic Editor (Eeschema)
   - Run ERC: `Inspect` → `Electrical Rules Checker`
   - Fix any schematic issues

5. **Update Gerbers:**
   - Menu: `File` → `Plot`
   - Generate new Gerber files
   - Review in Gerber Viewer

---

## Part 4: Design Improvements (Recommended)

### Power Distribution Enhancement

**Convert power traces to copper pours:**

1. **Add ground plane (if not present):**
   - Select bottom copper layer (B.Cu)
   - Menu: `Place` → `Filled Zone`
   - Draw zone covering entire board
   - Net: `GND`
   - Click `OK`

2. **Add +5V pour (top layer):**
   - Select top copper layer (F.Cu)
   - Draw zone for +5V distribution area
   - Net: `+5V`
   - Clearance: 0.5mm
   - Priority: Lower than GND

3. **Add thermal reliefs:**
   - Zone properties → `Thermal relief`
   - Spoke width: 0.4mm

### Signal Integrity

1. **Check I2C pull-ups:**
   - Verify 2.2kΩ - 4.7kΩ resistors present
   - Connected to SDA and SCL
   - Pull-up to appropriate voltage (3.3V or 5V)

2. **Add decoupling capacitors:**
   - Place 100nF ceramics near IC power pins
   - As close as possible (<5mm)
   - Ground via nearby

### Quality Checks

1. **Trace length matching (if needed):**
   - For differential pairs or high-speed signals
   - Use `Place` → `Tuning Pattern`

2. **Via stitching:**
   - Add vias connecting ground planes
   - Spacing: ~10-15mm
   - Around power components

---

## Quick Reference Commands

| Action | Keyboard Shortcut |
|--------|------------------|
| DRC | `Ctrl+Shift+I` |
| Edit Item | `E` |
| Move Item | `M` |
| Find | `Ctrl+F` |
| Route Track | `X` |
| 3D Viewer | `Alt+3` |
| Zoom to Selection | `F5` |
| Measure | `Ctrl+Shift+M` |

---

## Automated Fix Script (Advanced)

For advanced users, KiCad supports Python scripting:

```python
# kicad_fix_tracks.py
import pcbnew

board = pcbnew.GetBoard()

# Define width rules (in nanometers: 1mm = 1000000nm)
width_rules = {
    "+5V": 1000000,  # 1.0mm
    "Net-(Q1-G)": 300000,  # 0.3mm
    "Net-(Q2A-B1)": 250000,  # 0.25mm
    "/GPIO2/SDA1": 300000,  # 0.3mm
    "Net-(J6-Pin_2)": 250000  # 0.25mm
}

# Update track widths
for track in board.GetTracks():
    net_name = track.GetNetname()
    if net_name in width_rules:
        track.SetWidth(width_rules[net_name])
        print(f"Updated {net_name}: {track.GetWidth()/1000000}mm")

pcbnew.Refresh()
print("Track widths updated!")
```

**To run:**
1. In Pcbnew: `Tools` → `Scripting Console`
2. Paste and execute script
3. Save board
4. Run DRC to verify

---

## Troubleshooting

### Problem: Can't select tiny tracks
**Solution:** Zoom in more (`Mouse wheel` or `F1/F2`)

### Problem: Track won't change width
**Solution:** Check if track is locked. Press `L` to toggle lock.

### Problem: DRC still shows errors after fix
**Solution:** 
- Refresh DRC: close and reopen DRC window
- Save file and reopen KiCad
- Check if you modified all segments of multi-segment track

### Problem: Silkscreen moves back
**Solution:** 
- Lock reference position after moving
- Check if "Auto-place" is enabled (disable it)

---

## Estimated Time

- **Track width fixes:** 30-45 minutes
- **Silkscreen fixes:** 15-20 minutes  
- **Verification:** 10-15 minutes
- **Design improvements:** 1-2 hours (optional)

**Total:** ~1 to 3 hours depending on thoroughness

---

## Success Criteria

- [ ] All 12 track width violations cleared
- [ ] All 4 silkscreen violations cleared
- [ ] DRC shows 0 errors
- [ ] 3D view looks correct
- [ ] Gerber files generated successfully
- [ ] Assembly can proceed to manufacturing

---

## Next Steps After Fixing

1. Generate manufacturing files
2. Review Gerber files in viewer
3. Generate BOM (Bill of Materials)
4. Create assembly drawing
5. Order PCBs from manufacturer

Good luck! 🎯
