#!/usr/bin/env python3
"""
KiCad DRC Master Fixer
Runs all automated DRC fixes for the MbW Lathe HAT PCB

This script:
1. Fixes track width violations (12 errors)
2. Fixes silkscreen overlap violations (4 errors)
3. Verifies changes
4. Provides summary

Usage in KiCad Scripting Console:
    exec(open('/path/to/fix_all_drc_errors.py').read())
"""

import pcbnew
import sys
import os

def main():
    """Run all DRC fixes"""
    print("=" * 80)
    print("MbW Lathe HAT - DRC Master Fixer")
    print("=" * 80)
    print()
    
    board = pcbnew.GetBoard()
    
    if not board:
        print("❌ ERROR: No board loaded!")
        print("Please open hat.kicad_pcb in KiCad Pcbnew first.")
        return False
    
    print(f"📋 Board: {board.GetFileName()}")
    print(f"📊 Total DRC Errors to Fix: 16")
    print(f"   - Track width violations: 12")
    print(f"   - Silkscreen overlaps: 4")
    print()
    
    input("Press Enter to continue with automated fixes (Ctrl+C to cancel)...")
    print()
    
    # Import the fix modules
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    success_track = False
    success_silk = False
    
    # Fix 1: Track Widths
    print("=" * 80)
    print("STEP 1: Fixing Track Widths")
    print("=" * 80)
    print()
    
    try:
        # Import and run track width fixer
        track_fixer_path = os.path.join(script_dir, 'fix_drc_track_widths.py')
        
        if os.path.exists(track_fixer_path):
            with open(track_fixer_path, 'r') as f:
                exec(f.read(), globals())
            success_track = fix_track_widths()  # Function from imported script
        else:
            print("⚠ Warning: fix_drc_track_widths.py not found")
            print(f"Expected at: {track_fixer_path}")
            # Try to run inline version
            success_track = fix_track_widths_inline()
    except Exception as e:
        print(f"❌ Error fixing track widths: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Fix 2: Silkscreen Overlaps
    print("=" * 80)
    print("STEP 2: Fixing Silkscreen Overlaps")
    print("=" * 80)
    print()
    
    try:
        # Import and run silkscreen fixer
        silk_fixer_path = os.path.join(script_dir, 'fix_drc_silkscreen.py')
        
        if os.path.exists(silk_fixer_path):
            with open(silk_fixer_path, 'r') as f:
                exec(f.read(), globals())
            success_silk = fix_silkscreen_overlaps()  # Function from imported script
        else:
            print("⚠ Warning: fix_drc_silkscreen.py not found")
            print(f"Expected at: {silk_fixer_path}")
            # Try to run inline version
            success_silk = fix_silkscreen_overlaps_inline()
    except Exception as e:
        print(f"❌ Error fixing silkscreen: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    if success_track and success_silk:
        print("✅ All automated fixes completed successfully!")
        print()
        print("Next steps:")
        print("1. ✓ Track widths updated")
        print("2. ✓ Silkscreen references repositioned")
        print("3. ⏳ SAVE the board (File → Save or Ctrl+S)")
        print("4. ⏳ Run DRC (Inspect → Design Rules Checker)")
        print("5. ⏳ Verify all 16 errors are resolved")
        print("6. ⏳ Visual inspection in 3D viewer (Alt+3)")
        print("7. ⏳ Generate Gerber files")
        print()
        print("💡 Tip: If DRC still shows errors, they may need manual adjustment.")
        
        # Refresh display
        pcbnew.Refresh()
        return True
        
    elif success_track:
        print("⚠ Partial success: Track widths fixed, but silkscreen fix failed")
        print("Please fix silkscreen overlaps manually (see DRC_FIX_PROCEDURE.md)")
        return False
        
    elif success_silk:
        print("⚠ Partial success: Silkscreen fixed, but track width fix failed")
        print("Please fix track widths manually (see DRC_FIX_PROCEDURE.md)")
        return False
        
    else:
        print("❌ Automated fixes failed")
        print("Please follow manual procedure in DRC_FIX_PROCEDURE.md")
        return False

def fix_track_widths_inline():
    """Inline version of track width fixer"""
    from fix_drc_track_widths import fix_track_widths
    return fix_track_widths()

def fix_silkscreen_overlaps_inline():
    """Inline version of silkscreen fixer"""
    from fix_drc_silkscreen import fix_silkscreen_overlaps
    return fix_silkscreen_overlaps()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
