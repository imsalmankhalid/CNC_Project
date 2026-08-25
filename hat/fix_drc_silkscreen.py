#!/usr/bin/env python3
"""
KiCad PCB Silkscreen Overlap Fixer
Automatically repositions component reference designators to fix silkscreen DRC violations

Usage:
1. Open KiCad Pcbnew
2. Go to Tools → Scripting Console
3. Run: exec(open('/path/to/fix_drc_silkscreen.py').read())
"""

import pcbnew
import sys

# Define reference repositioning rules
# Format: 'Reference': (x_offset_mm, y_offset_mm, rotation_change)
REFERENCE_ADJUSTMENTS = {
    'R7': (0, -2.0, 0),  # Move up 2mm
    'R5': (2.0, 0, 0),   # Move right 2mm
    'R6': (0, -2.0, 0),  # Move up 2mm
    'C4': (0, 2.0, 0),   # Move down 2mm (away from C3)
}

# Components that are having overlap issues (for verification)
PROBLEM_PAIRS = [
    ('R7', 'R8'),
    ('R7', 'R5'),
    ('R6', 'R5'),
    ('C4', 'C3'),
]

def mm_to_nm(millimeters):
    """Convert millimeters to nanometers (KiCad internal unit)"""
    return int(millimeters * 1000000)

def nm_to_mm(nanometers):
    """Convert nanometers to millimeters"""
    return nanometers / 1000000.0

def fix_silkscreen_overlaps():
    """Fix silkscreen overlaps by repositioning reference designators"""
    try:
        board = pcbnew.GetBoard()
        
        if not board:
            print("ERROR: No board loaded!")
            print("Please open the PCB file in KiCad first.")
            return False
        
        print("=" * 60)
        print("KiCad PCB Silkscreen Overlap Fixer")
        print("=" * 60)
        print(f"Board: {board.GetFileName()}")
        print()
        
        footprints_updated = 0
        footprints_found = set()
        
        # Iterate through all footprints
        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            
            if ref in REFERENCE_ADJUSTMENTS:
                # Get current reference field
                ref_field = footprint.Reference()
                
                # Get current position
                current_pos = ref_field.GetPosition()
                current_x_mm = nm_to_mm(current_pos.x)
                current_y_mm = nm_to_mm(current_pos.y)
                current_rotation = ref_field.GetTextAngle().AsDegrees()
                
                # Get adjustment
                x_offset_mm, y_offset_mm, rotation_change = REFERENCE_ADJUSTMENTS[ref]
                
                # Calculate new position
                new_x_nm = mm_to_nm(current_x_mm + x_offset_mm)
                new_y_nm = mm_to_nm(current_y_mm + y_offset_mm)
                new_pos = pcbnew.VECTOR2I(new_x_nm, new_y_nm)
                
                # Calculate new rotation
                new_rotation = current_rotation + rotation_change
                
                print(f"Updating: {ref}")
                print(f"  Current position: ({current_x_mm:.2f}, {current_y_mm:.2f}) mm")
                print(f"  Offset: ({x_offset_mm:.2f}, {y_offset_mm:.2f}) mm")
                print(f"  New position: ({nm_to_mm(new_x_nm):.2f}, {nm_to_mm(new_y_nm):.2f}) mm")
                
                if rotation_change != 0:
                    print(f"  Rotation: {current_rotation}° → {new_rotation}°")
                
                # Apply changes
                ref_field.SetPosition(new_pos)
                
                if rotation_change != 0:
                    ref_field.SetTextAngle(pcbnew.EDA_ANGLE(new_rotation, pcbnew.DEGREES_T))
                
                footprints_updated += 1
                footprints_found.add(ref)
                print()
        
        print("=" * 60)
        print("Summary:")
        print(f"  Footprints updated: {footprints_updated}")
        print()
        
        if footprints_found:
            print("Updated references:")
            for ref in sorted(footprints_found):
                print(f"  - {ref}")
        
        # Check for missing references
        expected_refs = set(REFERENCE_ADJUSTMENTS.keys())
        missing_refs = expected_refs - footprints_found
        if missing_refs:
            print()
            print("⚠ Warning: Expected references not found:")
            for ref in sorted(missing_refs):
                print(f"  - {ref}")
        
        print("=" * 60)
        
        if footprints_updated > 0:
            print()
            print("✓ Reference positions updated successfully!")
            print()
            print("Next steps:")
            print("1. Visually inspect the changed references")
            print("2. Adjust manually if needed (select, press M to move)")
            print("3. Save the board (File → Save or Ctrl+S)")
            print("4. Run DRC (Inspect → Design Rules Checker)")
            print("5. Verify silkscreen overlap errors are resolved")
            
            # Refresh the display
            pcbnew.Refresh()
            return True
        else:
            print()
            print("No references needed updating.")
            return True
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def list_component_positions():
    """List positions of components involved in overlaps"""
    try:
        board = pcbnew.GetBoard()
        
        if not board:
            print("ERROR: No board loaded!")
            return
        
        print("=" * 80)
        print("Component Positions (Problem Areas):")
        print("=" * 80)
        
        # Collect all references mentioned in problems
        all_refs = set()
        for ref1, ref2 in PROBLEM_PAIRS:
            all_refs.add(ref1)
            all_refs.add(ref2)
        
        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            
            if ref in all_refs:
                # Get footprint position
                fp_pos = footprint.GetPosition()
                fp_x_mm = nm_to_mm(fp_pos.x)
                fp_y_mm = nm_to_mm(fp_pos.y)
                fp_rotation = footprint.GetOrientationDegrees()
                
                # Get reference field position
                ref_field = footprint.Reference()
                ref_pos = ref_field.GetPosition()
                ref_x_mm = nm_to_mm(ref_pos.x)
                ref_y_mm = nm_to_mm(ref_pos.y)
                ref_rotation = ref_field.GetTextAngle().AsDegrees()
                
                print(f"\n{ref}:")
                print(f"  Footprint: ({fp_x_mm:.2f}, {fp_y_mm:.2f}) mm, {fp_rotation}°")
                print(f"  Reference: ({ref_x_mm:.2f}, {ref_y_mm:.2f}) mm, {ref_rotation}°")
                print(f"  Value: {footprint.GetValue()}")
        
        print("\n" + "=" * 80)
        print("\nProblem pairs:")
        for ref1, ref2 in PROBLEM_PAIRS:
            print(f"  {ref1} overlaps {ref2}")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def check_clearances():
    """Check clearances between components involved in overlaps"""
    try:
        board = pcbnew.GetBoard()
        
        if not board:
            print("ERROR: No board loaded!")
            return
        
        print("=" * 80)
        print("Clearance Check:")
        print("=" * 80)
        
        # Build a dictionary of footprint positions
        footprints = {}
        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            ref_field = footprint.Reference()
            ref_pos = ref_field.GetPosition()
            
            footprints[ref] = {
                'position': (nm_to_mm(ref_pos.x), nm_to_mm(ref_pos.y)),
                'size': (nm_to_mm(ref_field.GetTextWidth()), nm_to_mm(ref_field.GetTextHeight())),
            }
        
        # Check problem pairs
        for ref1, ref2 in PROBLEM_PAIRS:
            if ref1 in footprints and ref2 in footprints:
                pos1 = footprints[ref1]['position']
                pos2 = footprints[ref2]['position']
                
                # Calculate distance between reference centers
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                distance = (dx**2 + dy**2)**0.5
                
                print(f"\n{ref1} ↔ {ref2}:")
                print(f"  Distance: {distance:.2f} mm")
                print(f"  Δx: {dx:.2f} mm")
                print(f"  Δy: {dy:.2f} mm")
                
                if distance < 2.0:
                    print(f"  ⚠ WARNING: Very close! (< 2mm)")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nKiCad PCB Silkscreen Overlap Fixer\n")
    
    # Uncomment to see component positions first:
    # list_component_positions()
    # print("\n")
    # check_clearances()
    # print("\n")
    
    # Fix the silkscreen overlaps
    success = fix_silkscreen_overlaps()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
