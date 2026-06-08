# MbW Lathe HMI — User Interface Guide

**Software version:** RPi Edition (ported from Arduino v0.5.25 alpha0.1)
**Display target:** 800 × 480 capacitive touchscreen

---

## Screen Overview

The HMI has five screens accessible by touch:

```
┌─────────────────────────────────────────────┐
│  1. Main DRO Screen  ← default on power-on  │
│  2. Mode Select                              │
│  3. Thread Cutting Wizard                    │
│  4. Profile / Taper Wizard                   │
│  5. Radius / Sphere Wizard                   │
└─────────────────────────────────────────────┘
```

Navigation: tap **MODES ▶** from Screen 1 to reach Screen 2. From Screen 2 tap a mode to enter it, or tap **← Back** to return to the DRO.

---

## Screen 1 — Main DRO Screen

This is the primary operating screen shown during normal handwheel use.

### Layout

```
┌──────────────────────────────┬──────────┬──────────────────┐
│ X  +000.0000 mm   M1        │  RPM     │  Z-STOP          │
│ ──────────────────────────── │  1234    │  -123.456 mm     │
│ Z  -000.000  mm   M1        │  ────    │  ────────        │
│                              │  IPM     │  LIMITS          │
│                              │  12.5    │ ◉Z+  ◉Z-         │
│                              │          │ ◉X+  ◉X-         │
├──────────────────────────────┴──────────┴──────────────────┤
│ [X M1▶] [ZERO X] [Z M1▶] [ZERO Z] [mm/in] [SET STOP]      │
│ [CLR STOP]  [MODES ▶]                          [⬛ E-STOP] │
└─────────────────────────────────────────────────────────────┘
```

### DRO Panel (top-left)

| Display element | Description |
|---|---|
| **X  ±xxx.xxxx mm** | X-axis position relative to active X memory zero. 4 decimal places in mm, 5 in inch. |
| **Z  ±xxx.xxx mm** | Z-axis position relative to active Z memory zero. 3 decimal places in mm, 4 in inch. |
| **M1 / M2 / M3** (right of value) | Active memory slot badge — shows which zero reference is currently in use. |

### Speed & Feed Panel (top-centre)

| Display element | Description |
|---|---|
| **RPM** | Live spindle speed calculated from index pulse. Updates whenever spindle speed changes by >2 RPM. Shows 0 when spindle is stopped. |
| **IPM** | Feed rate in inches per minute, as set by the potentiometer (feed rate knob). Converts to mm/min internally for motion. |

### Status Panel (top-right)

| Display element | Description |
|---|---|
| **Z-STOP** | Shows the Z auto-stop target position relative to the active Z zero. Displays `Not Set` until a stop is set with **SET STOP**. Displays `+++>>>` if the carriage is already past the stop target. |
| **LIMITS  ◉Z+  ◉Z-  ◉X+  ◉X-** | Limit switch indicators. Green `◉` = switch OK (not triggered). Red `⬛` = switch triggered (motion blocked). |

---

### Button Bar — All Functions

#### Memory & Zero Functions

| Button | Label | What it does | Arduino equivalent |
|---|---|---|---|
| **X M1 ▶** | Shows current X slot | Cycles X-axis memory slot: M1 → M2 → M3 → M1. The DRO immediately shows position relative to the newly selected memory's zero. | Button 1 — short press |
| **ZERO X** | Zero X | Sets the current X motor position as the zero reference for the **active X memory slot** (e.g. M1). The DRO resets to 0.0000. | Button 1 — long press (hold) |
| **Z M1 ▶** | Shows current Z slot | Cycles Z-axis memory slot: M1 → M2 → M3 → M1. | Button 2 — short press |
| **ZERO Z** | Zero Z | Sets the current Z motor position as the zero reference for the **active Z memory slot**. | Button 2 — long press (hold) |

> **How memory slots work:**  
> There are 3 independent zero references per axis (M1, M2, M3). Each slot remembers a different zero position. For example: set M1 to the left end of the part, M2 to a shoulder, M3 to the chuck face. Switch between them instantly without losing any reference.  
> The **X Mx ▶** / **Z Mx ▶** button label updates to always show the currently active slot number.

#### Unit Toggle

| Button | What it does | Arduino equivalent |
|---|---|---|
| **mm / in** | Toggles between millimetre and inch display. Affects both DRO values and the Z-STOP display. Feed rate (IPM) is always shown in imperial. | Button 3 — short press (<600 ms) |

#### Z Auto-Stop Functions

| Button | What it does | Arduino equivalent |
|---|---|---|
| **SET STOP** | Records the **current Z position** as the auto-stop target for the active Z memory slot. The half-nut electronic feed will halt automatically when the carriage reaches this position. | Button 3 — medium press (600–1800 ms) |
| **CLR STOP** | Clears the Z-stop target. Status panel returns to `Not Set`. Feed will run freely until manually disengaged. | *(Not in Arduino — was achieved by zeroing Z then re-setting stop)* |

#### Mode Navigation

| Button | What it does | Arduino equivalent |
|---|---|---|
| **MODES ▶** | Opens the Mode Select screen to switch to Thread Cutting, Profile/Taper, or Radius/Sphere mode. | Button 3 — long press (>1800 ms) |

#### Emergency Stop

| Button | What it does | Notes |
|---|---|---|
| **⬛ E-STOP** | Immediately sets the `estop` flag. All motor motion halts. Button turns solid red and text changes to **⚠ RESET ESTOP**. | Tap again to reset the E-stop flag and resume operation. On the real RPi this is hardware-wired in addition to the software flag. |

---

## Screen 2 — Mode Select

```
┌──────────────────────────────────────────┐
│          Select Operating Mode           │
│  ┌──────────────┐  ┌──────────────┐      │
│  │  ◎           │  │  ⟨⟩          │      │
│  │  DRO         │  │  Thread      │      │
│  │  Handwheel   │  │  Cutting     │      │
│  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐      │
│  │  △           │  │  ◔           │      │
│  │  Profile     │  │  Radius      │      │
│  │  / Taper     │  │  / Sphere    │      │
│  └──────────────┘  └──────────────┘      │
│  [← Back]                                │
└──────────────────────────────────────────┘
```

| Button | What it does |
|---|---|
| **◎ DRO Handwheel** | Returns to the main DRO screen (same as **← Back**). |
| **⟨⟩ Thread Cutting** | Enters the threading wizard. Resets all threading parameters. |
| **△ Profile / Taper** | Enters the profile/taper wizard. |
| **◔ Radius / Sphere** | Enters the radius/arc turning wizard. |
| **← Back** | Returns to the main DRO screen without changing mode. |

---

## Screen 3 — Thread Cutting Wizard

Guides the operator through a complete thread cutting setup and execution. Equivalent to the full `40_Thread.ino` state machine in the Arduino code.

### Live DRO Strip
The X and Z axis positions are always visible at the top of this screen, updating at 10 Hz. This allows the operator to position the tool while reading the screen.

### Wizard Steps

| Step | Screen shows | Buttons active | What to do |
|---|---|---|---|
| 1 | **Thread Size** — e.g. `M10x1.5` | ▼ PREV  ▲ NEXT  ✓ ACCEPT | Use ▼/▲ to scroll through the 17 thread sizes, tap ✓ ACCEPT to confirm. |
| 2 | **Material** — e.g. `Mild Steel` | ▼ PREV  ▲ NEXT  ✓ ACCEPT | Select workpiece material (affects recommended RPM). |
| 3 | **Cutting Tool** — `HSS` / `Carbide` | ▼ PREV  ▲ NEXT  ✓ ACCEPT | Select tool material. |
| 4 | **Turn OD** | ✓ ACCEPT | Turn the nominal OD and measure it. Enter your measured OD if prompted, then confirm. |
| 5 | **Set C391 Tool** | ✓ ACCEPT | Move the C391 gauge tool until it just touches the OD surface. Tap ✓ ACCEPT to record the position. |
| 6 | **Set Tool Tip** | ✓ ACCEPT | Touch the threading cutter tip to the OD surface. Tap ✓ ACCEPT. |
| 7 | **Set X Retract** | ✓ ACCEPT | Move X axis to the retract (clearance) position. Tap ✓ ACCEPT. |
| 8 | **Set Z End** | ✓ ACCEPT | Move Z to the **end** of the thread (where cutting stops). Tap ✓ ACCEPT. |
| 9 | **Set Z Start** | ✓ ACCEPT | Move Z to the **start** of the thread. Tap ✓ ACCEPT. |
| 10 | **Run Pass** — shows pass number, recommended RPM | ▶ RUN PASS | Tap **▶ RUN PASS** to execute the next threading pass. The carriage traverses from Z start to Z end automatically. |
| 11 | **Pass Complete** | ▶ RUN PASS | Runs again for spring passes (default 2). Repeat until all passes complete. |

| Button | Visible when | What it does |
|---|---|---|
| **▼ PREV** | Selection steps (size, material, tool) | Moves to previous item in list |
| **▲ NEXT** | Selection steps | Moves to next item in list |
| **✓ ACCEPT** | All steps except RUN | Confirms current value/position and advances to next step |
| **▶ RUN PASS** | Pass execution steps | Triggers the thread cutting pass |
| **✕ EXIT** | Always | Aborts the wizard and returns to the main DRO screen |

### Built-in Thread Table (17 sizes)

| Imperial UNC/UNF | Metric |
|---|---|
| #4-40, #6-32, #8-32 | M6×1.0 |
| #10-24, #10-32 | M8×1.25 |
| 1/4"-20, 1/4"-28 | M10×1.5 |
| 5/16"-18, 5/16"-24 | M12×1.75 |
| 3/8"-16, 3/8"-24 | |
| 1/2"-13, 1/2"-20 | |

---

## Screen 4 — Profile / Taper Wizard

Cuts a multi-point profile, taper, or stepped contour. Equivalent to `50_Profile.ino`.

### Live DRO Strip
X and Z positions update at 10 Hz throughout the wizard.

### Wizard Steps

| Step | Screen shows | Buttons active | What to do |
|---|---|---|---|
| 1 | **Touch tool to stock OD** | ✓ OK | Touch cutting tool to stock surface, tap ✓ OK to record X stock position. |
| 2 | **Set X Retract** | ✓ OK | Move X to clearance position, tap ✓ OK. |
| 3 | **Number of profile points** | ▼  ▲  ✓ OK | Use ▼/▲ to select how many profile points (2–10). Tap ✓ OK. |
| 4–n | **Move to profile point N** | ✓ OK | Move tool to each profile point position, tap ✓ OK to record each. |
| DOC | **Depth of cut** | ▼  ▲  ✓ OK | Use ▼/▲ to set rough pass DOC in mm. Tap ✓ OK. |
| Run | **Profile running…** | (automatic) | Machine cuts automatically from point to point. Progress shows pass/total. |
| Done | **Profile complete!** | ✕ EXIT | Tap EXIT to return to main screen. |

| Button | What it does |
|---|---|
| **▼ / ▲** | Decrease / increase number of points or DOC value |
| **✓ OK** | Accept current position or value and advance |
| **✕ EXIT** | Abort and return to DRO screen |

---

## Screen 5 — Radius / Sphere Wizard

Cuts internal or external arcs and spherical forms. Equivalent to `60_Radius.ino`.

### Live DRO Strip
X and Z positions update at 10 Hz throughout the wizard.

### Wizard Steps

| Step | Screen shows | Buttons active | What to do |
|---|---|---|---|
| 1 | **Arc type** — External / Internal | ▼  ▲  ✓ OK | Select External (convex) or Internal (concave). |
| 2 | **Insert type** — Round / Ball-nose | ▼  ▲  ✓ OK | Select cutter insert type. |
| 3 | **Insert size** — confirm diameter | ▼  ▲  ✓ OK | Confirm insert radius/diameter. |
| 4 | **Touch tool to known OD** | ✓ OK | Touch tool to a known-diameter surface, tap ✓ OK. |
| 5 | **Set X retract** | ✓ OK | Move X to clearance, tap ✓ OK. |
| 6 | **Arc radius** | ▼  ▲  ✓ OK | Use ▼/▲ to enter desired radius. |
| 7 | **Touch tool to arc centre** | ✓ OK | Position tool at Z centre of arc, tap ✓ OK. |
| 8 | **Depth of cut** | ▼  ▲  ✓ OK | Set DOC per pass. |
| Run | **Arc running…** | (automatic) | Machine interpolates arc automatically. Shows pass/total. |
| Done | **Arc complete!** | ✕ EXIT | Tap EXIT to return to DRO screen. |

---

## Function Comparison: Arduino vs UI

| Function | Arduino | RPi UI screen | Button / How |
|---|---|---|---|
| X axis DRO display | LCD row 0: X value | Main DRO panel | Live — always visible |
| Z axis DRO display | LCD row 1: Z value | Main DRO panel | Live — always visible |
| Spindle RPM display | LCD row 2: `RPM = xxxx` | Speed panel | Live — always visible |
| Feed rate display | LCD row 3: `IPM = xx.x` | Speed panel | Live — always visible |
| Z-STOP display | LCD row 3, right side | Status panel | Live — always visible |
| Limit switch display | *(not on LCD)* | Status panel ◉/⬛ | Live — always visible |
| Cycle X memory slot | Button 1 short press | **X M1 ▶** | Tap cycles M1→M2→M3→M1 |
| Zero X axis | Button 1 long hold | **ZERO X** | Tap to zero at current position |
| Cycle Z memory slot | Button 2 short press | **Z M1 ▶** | Tap cycles M1→M2→M3→M1 |
| Zero Z axis | Button 2 long hold | **ZERO Z** | Tap to zero at current position |
| Toggle mm ↔ inch | Button 3 short press | **mm / in** | Tap toggles units |
| Set Z auto-stop | Button 3 medium hold | **SET STOP** | Tap to mark current Z as stop target |
| Clear Z auto-stop | *(workaround only)* | **CLR STOP** | Tap to remove stop (new in RPi version) |
| Enter mode select | Button 3 long hold | **MODES ▶** | Tap to open mode selection screen |
| Thread cutting mode | Mode selection | Screen 3 | Via MODES ▶ → Thread Cutting |
| Profile/taper mode | Mode selection | Screen 4 | Via MODES ▶ → Profile/Taper |
| Radius/sphere mode | Mode selection | Screen 5 | Via MODES ▶ → Radius/Sphere |
| Return to DRO from mode | *(auto on mode exit)* | **✕ EXIT** in each wizard | Always visible in wizard screens |
| E-Stop | Hardware button (wired to servo ENABLE) | **⬛ E-STOP** button | Software flag + hardware wiring on RPi |
| Live DRO in wizard | *(LCD not updated during wizards)* | DRO strip at top of each wizard | Updates at 10 Hz — new in RPi version |

---

## Quick Reference Card

```
MAIN SCREEN
───────────────────────────────────────────────────────
X Mx ▶         Cycle X memory slot  (M1 → M2 → M3 → M1)
ZERO X         Set current X position as zero for active slot
Z Mx ▶         Cycle Z memory slot
ZERO Z         Set current Z position as zero for active slot
mm / in        Toggle display units
SET STOP       Mark current Z position as auto-stop target
CLR STOP       Remove auto-stop target
MODES ▶        Open mode selection
⬛ E-STOP      Emergency stop (tap again to reset)

MODE SELECT
───────────────────────────────────────────────────────
◎ DRO          Return to handwheel operation
⟨⟩ Thread      Start thread cutting wizard
△ Profile      Start profile/taper wizard
◔ Radius       Start radius/sphere wizard
← Back         Cancel, return to DRO

WIZARD CONTROLS (Thread / Profile / Radius)
───────────────────────────────────────────────────────
▼ / ▲          Scroll through options or adjust value
✓ OK / ACCEPT  Confirm current value and proceed
▶ RUN PASS     Execute cutting pass (threading only)
✕ EXIT         Abort wizard, return to main DRO screen
```

---

## Notes

- **Memory slots** (M1/M2/M3) are independent zero references. Each axis has its own 3 slots. Switching slots does not move the machine — it only changes which zero the DRO reads against.
- **Z-STOP is per memory slot.** If you switch from M1 to M2, the stop display updates to M2's stop value.
- **Zeroing does not clear the stop.** Use **CLR STOP** to explicitly remove a set stop point.
- **Feed rate** is controlled by the physical potentiometer knob, not by on-screen buttons. The IPM value shown is read-only.
- **E-STOP** in mock mode (desktop testing) only sets a software flag. On the real RPi the ENABLE pins to the servo drives must also be wired to the E-stop circuit.
