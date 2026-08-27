#!/usr/bin/env python3
"""
KiCad PCB Track Width Fixer
Automatically fixes track width DRC violations in hat.kicad_pcb

Usage:
1. Open KiCad Pcbnew
2. Go to Tools → Scripting Console
3. Run: exec(open('/path/to/fix_drc_track_widths.py').read())

Or from command line (if KiCad Python API is installed):
python3 fix_drc_track_widths.py
"""

import pcbnew
import sys

# Define track width rules based on DRC analysis
# Values in millimeters
TRACK_WIDTH_RULES = {
    "+5V": 1.0,  # Power distribution - CRITICAL
    "Net-(Q1-G)": 0.3,  # MOSFET/Transistor gate - needs noise immunity
    "Net-(Q2A-B1)": 0.25,  # Transistor base
    "/GPIO2/SDA1": 0.3,  # I2C data line - signal integrity
    "/GPIO2{slash}SDA1": 0.3,  # Alternative encoding
    "Net-(J6-Pin_2)": 0.25,  # Connector signal (adjust if power)
}

# Minimum width for any track (design rule)
MINIMUM_TRACK_WIDTH = 0.2  # mm

def nm_to_mm(nanometers):
    """Convert nanometers to millimeters"""
    return nanometers / 1000000.0

def mm_to_nm(millimeters):
    """Convert millimeters to nanometers (KiCad internal unit)"""
    return int(millimeters * 1000000)

def fix_track_widths():
    """Fix all track widths according to rules"""
    try:
        board = pcbnew.GetBoard()
        
        if not board:
            print("ERROR: No board loaded!")
            print("Please open the PCB file in KiCad first.")
            return False
        
        print("=" * 60)
        print("KiCad PCB Track Width Fixer")
        print("=" * 60)
        print(f"Board: {board.GetFileName()}")
        print()
        
        # Statistics
        tracks_checked = 0
        tracks_updated = 0
        nets_found = set()
        
        # Get all tracks (this includes segments and arcs)
        for track in board.GetTracks():
            tracks_checked += 1
            net = track.GetNet()
            
            if not net:
                continue
            
            net_name = net.GetNetname()
            current_width_mm = nm_to_mm(track.GetWidth())
            
            # Check if this net has a specific rule
            if net_name in TRACK_WIDTH_RULES:
                required_width_mm = TRACK_WIDTH_RULES[net_name]
                required_width_nm = mm_to_nm(required_width_mm)
                
                if track.GetWidth() != required_width_nm:
                    print(f"Updating: {net_name}")
                    print(f"  Current: {current_width_mm:.3f} mm")
                    print(f"  New:     {required_width_mm:.3f} mm")
                    
                    track.SetWidth(required_width_nm)
                    tracks_updated += 1
                    nets_found.add(net_name)
            
            # Check minimum width for all tracks
            elif current_width_mm < MINIMUM_TRACK_WIDTH:
                print(f"Warning: Track on net '{net_name}' below minimum")
                print(f"  Current: {current_width_mm:.3f} mm")
                print(f"  Minimum: {MINIMUM_TRACK_WIDTH:.3f} mm")
                print(f"  Updating to minimum...")
                
                track.SetWidth(mm_to_nm(MINIMUM_TRACK_WIDTH))
                tracks_updated += 1
        
        print()
        print("=" * 60)
        print("Summary:")
        print(f"  Total tracks checked: {tracks_checked}")
        print(f"  Tracks updated: {tracks_updated}")
        print(f"  Nets updated: {len(nets_found)}")
        print()
        
        if nets_found:
            print("Updated nets:")
            for net in sorted(nets_found):
                print(f"  - {net}")
        
        # Check for missing nets
        expected_nets = set(TRACK_WIDTH_RULES.keys())
        missing_nets = expected_nets - nets_found
        if missing_nets:
            print()
            print("⚠ Warning: Expected nets not found:")
            for net in sorted(missing_nets):
                print(f"  - {net}")
                print(f"    (Check if net name in schematic matches)")
        
        print("=" * 60)
        
        if tracks_updated > 0:
            print()
            print("✓ Track widths updated successfully!")
            print()
            print("Next steps:")
            print("1. Save the board (File → Save or Ctrl+S)")
            print("2. Run DRC (Inspect → Design Rules Checker)")
            print("3. Verify all track width errors are resolved")
            print("4. Check for any new violations")
            
            # Refresh the display
            pcbnew.Refresh()
            return True
        else:
            print()
            print("No tracks needed updating.")
            print("All tracks already meet minimum requirements.")
            return True
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def list_all_nets():
    """List all nets in the design with track count and widths"""
    try:
        board = pcbnew.GetBoard()
        
        if not board:
            print("ERROR: No board loaded!")
            return
        
        print("=" * 80)
        print("All Nets in Design:")
        print("=" * 80)
        
        net_info = {}
        
        for track in board.GetTracks():
            net = track.GetNet()
            if not net:
                continue
            
            net_name = net.GetNetname()
            width_mm = nm_to_mm(track.GetWidth())
            
            if net_name not in net_info:
                net_info[net_name] = {
                    'count': 0,
                    'widths': set(),
                    'min_width': width_mm,
                    'max_width': width_mm
                }
            
            net_info[net_name]['count'] += 1
            net_info[net_name]['widths'].add(width_mm)
            net_info[net_name]['min_width'] = min(net_info[net_name]['min_width'], width_mm)
            net_info[net_name]['max_width'] = max(net_info[net_name]['max_width'], width_mm)
        
        # Sort by net name
        for net_name in sorted(net_info.keys()):
            info = net_info[net_name]
            print(f"\nNet: {net_name}")
            print(f"  Segments: {info['count']}")
            print(f"  Width range: {info['min_width']:.3f} - {info['max_width']:.3f} mm")
            if len(info['widths']) > 1:
                print(f"  ⚠ Multiple widths: {sorted(info['widths'])}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nKiCad PCB Track Width Fixer\n")
    
    # Uncomment to see all nets first:
    # list_all_nets()
    # print("\n")
    
    # Fix the tracks
    success = fix_track_widths()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
