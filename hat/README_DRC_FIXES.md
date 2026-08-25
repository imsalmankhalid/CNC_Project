# DRC Error Fix - README

**PCB:** MbW Lathe Control HAT  
**Date:** 2026-08-11  
**DRC Errors:** 16 total (12 track width + 4 silkscreen overlap)

---

## Quick Start

### Option 1: Automated Fix (Recommended)

**In KiCad Pcbnew:**

1. Open `hat.kicad_pcb` in KiCad Pcbnew
2. Go to `Tools` → `Scripting Console`
3. Run:
   ```python
   exec(open('fix_all_drc_errors.py').read())
   ```
4. Follow the prompts
5. Save the board
6. Run DRC to verify

### Option 2: Individual Fixes

**Fix track widths only:**
```python
exec(open('fix_drc_track_widths.py').read())
```

**Fix silkscreen overlaps only:**
```python
exec(open('fix_drc_silkscreen.py').read())
```

### Option 3: Manual Fix

Follow the detailed procedure in [`DRC_FIX_PROCEDURE.md`](DRC_FIX_PROCEDURE.md)

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `DRC.json` | Original DRC error report from KiCad |
| `DRC_Analysis_and_Resolution.md` | Detailed analysis of all errors |
| `DRC_FIX_PROCEDURE.md` | Step-by-step manual fix guide |
| `fix_all_drc_errors.py` | Master script - runs all fixes |
| `fix_drc_track_widths.py` | Automated track width fixer |
| `fix_drc_silkscreen.py` | Automated silkscreen overlap fixer |
| `README_DRC_FIXES.md` | This file |

---

## Error Summary

### Track Width Errors (12)

| Net | Violations | Current | Required | Priority |
|-----|------------|---------|----------|----------|
| +5V | 2 | 0.15mm | 1.0mm | CRITICAL |
| /GPIO2/SDA1 | 2 | 0.15mm | 0.3mm | High |
| Net-(Q1-G) | 4 | 0.15mm | 0.25mm | High |
| Net-(Q2A-B1) | 2 | 0.15mm | 0.25mm | High |
| Net-(J6-Pin_2) | 2 | 0.15mm | 0.25mm | Medium |

**Total:** 12 violations

### Silkscreen Overlap Errors (4)

| Component Pair | Issue |
|----------------|-------|
| R7 ↔ R8 | Reference overlaps silkscreen |
| R7 ↔ R5 | Silkscreen overlaps reference |
| R6 ↔ R5 | Reference overlaps silkscreen |
| C4 ↔ C3 | Reference overlaps silkscreen |

**Total:** 4 violations

---

## How the Automated Scripts Work

### Track Width Fixer (`fix_drc_track_widths.py`)

**What it does:**
- Scans all copper tracks in the PCB
- Identifies tracks on specific nets (power, signals, etc.)
- Updates track widths according to rules:
  - Power (+5V): 1.0mm
  - I2C (SDA1): 0.3mm
  - Control signals: 0.25-0.3mm
- Ensures all tracks meet 0.2mm minimum

**How it works:**
1. Uses KiCad Python API (`pcbnew`)
2. Iterates through `board.GetTracks()`
3. Checks each track's net name
4. Updates width using `track.SetWidth()`
5. Refreshes display

### Silkscreen Fixer (`fix_drc_silkscreen.py`)

**What it does:**
- Repositions component reference labels
- Moves R7, R5, R6, C4 references to avoid overlaps
- Maintains readability and manufacturing clarity

**How it works:**
1. Iterates through `board.GetFootprints()`
2. Finds references R7, R5, R6, C4
3. Applies position offsets to move labels
4. Updates using `ref_field.SetPosition()`
5. Refreshes display

---

## Troubleshooting

### "No board loaded" Error

**Solution:** Open the PCB file in KiCad Pcbnew first, then run the script.

### Script Not Found

**Solution:** Make sure you're running the script from the correct directory:
```python
import os
os.chdir('/path/to/hat/directory')
exec(open('fix_all_drc_errors.py').read())
```

### Changes Not Visible

**Solution:** 
1. The script calls `pcbnew.Refresh()` automatically
2. If still not visible, close and reopen the board
3. Make sure you saved after running the script

### DRC Still Shows Errors

**Possible causes:**
1. Script didn't run successfully - check console for errors
2. Net names don't match - verify in schematic
3. Some tracks may need manual adjustment
4. Need to save and reopen KiCad

**Solution:** Run DRC again, check remaining errors, and fix manually if needed.

---

## Verification Checklist

After running the automated fixes:

- [ ] All scripts completed without errors
- [ ] Board saved (Ctrl+S)
- [ ] DRC run shows 0 errors
- [ ] Visual inspection looks correct
- [ ] 3D view checked (Alt+3)
- [ ] Track widths verified for power nets (Use measuring tool)
- [ ] Silkscreen labels readable and clear
- [ ] No new violations introduced

---

## Advanced Usage

### List All Nets Before Fixing

```python
exec(open('fix_drc_track_widths.py').read())
list_all_nets()
```

### Check Component Positions

```python
exec(open('fix_drc_silkscreen.py').read())
list_component_positions()
```

### Customize Track Widths

Edit `fix_drc_track_widths.py` and modify the `TRACK_WIDTH_RULES` dictionary:

```python
TRACK_WIDTH_RULES = {
    "+5V": 1.5,  # Increase to 1.5mm for more current capacity
    "Net-(J6-Pin_2)": 0.5,  # Increase if it's a power signal
}
```

### Customize Reference Positions

Edit `fix_drc_silkscreen.py` and modify the `REFERENCE_ADJUSTMENTS` dictionary:

```python
REFERENCE_ADJUSTMENTS = {
    'R7': (0, -3.0, 0),  # Move up 3mm instead of 2mm
}
```

---

## Manual Fix Alternative

If automated scripts don't work or you prefer manual control:

1. Read [`DRC_FIX_PROCEDURE.md`](DRC_FIX_PROCEDURE.md)
2. Open PCB in KiCad
3. Open DRC window (Ctrl+Shift+I)
4. Double-click each error to zoom to it
5. Fix according to procedure document
6. Verify with DRC

**Estimated time:** 1-3 hours

---

## Design Recommendations

After fixing DRC errors, consider these improvements:

1. **Power Distribution**
   - Use copper polygon pours for +5V and GND
   - Reduces resistance and improves thermal performance

2. **Signal Integrity**
   - Add 100nF decoupling caps near ICs
   - Verify I2C pull-up resistor values (2.2kΩ - 4.7kΩ)

3. **Manufacturing**
   - Add fiducial marks for assembly
   - Include version number on silkscreen
   - Add test points for critical signals

See [`DRC_Analysis_and_Resolution.md`](DRC_Analysis_and_Resolution.md) for detailed recommendations.

---

## Next Steps

After all DRC errors are fixed:

1. ✓ Run ERC on schematic (Electrical Rules Check)
2. ✓ Generate Gerber files (File → Plot)
3. ✓ Review in Gerber viewer
4. ✓ Generate drill files
5. ✓ Export BOM (Bill of Materials)
6. ✓ Create assembly drawing
7. ✓ Order PCBs from manufacturer

---

## Support

For questions or issues:

1. Check the error message in KiCad Python console
2. Review [`DRC_Analysis_and_Resolution.md`](DRC_Analysis_and_Resolution.md)
3. Follow manual procedure in [`DRC_FIX_PROCEDURE.md`](DRC_FIX_PROCEDURE.md)
4. Consult KiCad documentation: https://docs.kicad.org/

---

## Version History

| Date | Author | Changes |
|------|--------|---------|
| 2026-08-11 | GitHub Copilot | Initial DRC analysis and automated fix scripts |

---

## License

These scripts are provided as-is for the MbW Lathe Control project.
Always backup your PCB files before running automated scripts.

**⚠️ IMPORTANT:** Always verify the changes after running automated scripts. Review the DRC results and visually inspect the board before sending to manufacturing.
