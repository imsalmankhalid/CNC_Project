# MbW Lathe Arduino Controller — System Description

**Original project:** Lathe_v0.5.25_alpha0.1  
**Created by:** Rob Wade — WadeODesign.com (2017)  
**Controller:** Arduino Mega 2560  
**Document purpose:** Complete technical description of all functions, operating principles, and hardware connections

---

## 1. System Overview

The MbW (Machine-by-Wire) lathe controller converts a conventional manual lathe into a servo-assisted CNC-style machine while keeping the operator fully in control via the original handwheels. It does **not** replace the handwheels — it amplifies them. Turning the X or Z handwheel causes a servo motor to drive the corresponding leadscrew at precisely the same rate, as if the carriage were directly coupled. The operator feels the handwheel but the servo does the mechanical work.

### What the system does

| Function | Description |
|---|---|
| **Handwheel following** | Servo motors track both X and Z encoder inputs in real time |
| **Digital Readout (DRO)** | 4×20 character LCD shows X/Z position, spindle RPM, and feed rate |
| **Axis memory / zeroing** | 3 independent zero-reference slots per axis (M1/M2/M3) |
| **Electronic feed (half-nut)** | Engage a lever to drive Z at a calibrated feed rate from the potentiometer |
| **Z auto-stop** | Carriage halts automatically at a preset Z position during half-nut feed |
| **Thread cutting** | Automated external thread cutting wizard |
| **Profile / taper turning** | Multi-point contour turning mode |
| **Radius / sphere turning** | Arc interpolation mode for internal/external arcs and spheres |

---

## 2. Hardware Components

### 2.1 Controller

| Component | Part | Notes |
|---|---|---|
| Microcontroller | Arduino Mega 2560 | Required — uses Mega-specific PORTA (D22–D29) for motor pulses |
| LCD | 4-row × 20-column I2C LCD | I2C address 0x3F (scan if different). SDA = D20, SCL = D21 |

### 2.2 Servo Motors & Drivers

| Component | Part | Notes |
|---|---|---|
| Z-axis servo | Teknic ClearPath SDSK | Step/Dir digital servo. Configured for 800 counts/rev in MSP software |
| X-axis servo | Teknic ClearPath SDSK | Same as above |
| Z-axis power supply | 70 V DC, ≥7 A | Shared between both motors |

### 2.3 Encoders

| Component | Part | Notes |
|---|---|---|
| Z-axis handwheel encoder | CUI AMT103-V | 2000 CPR quadrature. Connected to interrupt pins D2, D3 |
| X-axis handwheel encoder | CUI AMT103-V | Connected to interrupt pins D18, D19 |

### 2.4 Spindle Sensor

| Component | Part | Notes |
|---|---|---|
| Index pulse sensor | AutoTech C3 (or equivalent) | 1 pulse per revolution. Connected to D13 (interrupt). Used for RPM and thread synchronisation |

### 2.5 Inputs

| Component | Pin | Notes |
|---|---|---|
| Button 1 (X axis) | D49 | Momentary push-button, active HIGH. Cycles X memory / zeros X |
| Button 2 (Z axis) | D51 | Momentary push-button, active HIGH. Cycles Z memory / zeros Z |
| Button 3 (General) | D50 | Momentary push-button, active HIGH. Units / stop / mode select |
| Half-nut lever switch | D8 | Active HIGH when lever engaged |
| Feed rate potentiometer | A3 | 10 kΩ linear pot. Wiper to A3, ends to GND and 5V |

---

## 3. Wiring / Pin Assignment Summary

```
Arduino Mega 2560
═══════════════════════════════════════════════════════
 MOTORS (must use D22–D29 / PORTA on Mega)
  D22 ──── Z motor DIR pin (HIGH = negative direction)
  D23 ──── Z motor STEP pin
  D27 ──── Z motor ENABLE pin (active LOW = enabled)
  D24 ──── X motor DIR pin
  D25 ──── X motor STEP pin
  D26 ──── X motor ENABLE pin

 ENCODERS
  D2  ──── Z encoder channel A  (interrupt)
  D3  ──── Z encoder channel B  (interrupt)
  D18 ──── X encoder channel A  (interrupt)
  D19 ──── X encoder channel B  (interrupt)

 SPINDLE
  D13 ──── Spindle index pulse (interrupt, rising edge)

 BUTTONS
  D49 ──── Button 1 (X axis)        — 10kΩ pull-down, active HIGH
  D51 ──── Button 2 (Z axis)        — 10kΩ pull-down, active HIGH
  D50 ──── Button 3 (General)       — 10kΩ pull-down, active HIGH
  D8  ──── Half-nut lever switch    — 10kΩ pull-down, active HIGH

 ANALOGUE
  A3  ──── Potentiometer wiper      — 10kΩ pot, ends to GND/5V

 I2C (LCD)
  D20 (SDA) ──┬─── LCD SDA
  D21 (SCL) ──┼─── LCD SCL
              └─── 4.7kΩ pull-up resistors to 5V on each line

 POWER
  GND ──── All signal grounds common
  5V  ──── Buttons (via pull-downs), pot, LCD
  12V ──── Arduino Vin (recommended regulated 12V/1A)
  70V DC ── ClearPath servo power bus (both motors shared)
═══════════════════════════════════════════════════════
```

### 3.1 ClearPath SDSK Motor Connections

Each ClearPath motor has an 8-pin Molex Mini-fit connector. The relevant connections:

```
ClearPath SDSK (per motor)
─────────────────────────────────────────
 Pin A/STEP  ──── Arduino STEP pin (D23 or D25)
 Pin B/DIR   ──── Arduino DIR  pin (D22 or D24)
 Pin E/EN    ──── Arduino ENABLE pin (D27 or D26)
 Pin H/HLFB  ──── (optional) Hardware fault feedback
 GND         ──── Signal ground (common with Arduino GND)
 +5V / VCC   ──── 5V logic supply from Arduino
 HV+, HV–   ──── 70 V DC motor power bus
─────────────────────────────────────────
```

> **⚠ Important:** ClearPath STEP/DIR/ENABLE inputs expect 5V TTL. This is compatible with the Arduino Mega's 5V logic directly. **No level shifter required** in the original Arduino design.

### 3.2 Encoder Connections (CUI AMT103-V)

```
AMT103-V (per encoder)  →  Arduino Mega
───────────────────────────────────────
 Pin 1 (VCC) ──── 5V
 Pin 2 (GND) ──── GND
 Pin 5 (A)   ──── D2  (Z) or D18 (X)
 Pin 6 (B)   ──── D3  (Z) or D19 (X)
───────────────────────────────────────
```

> The AMT103-V is 5V compatible. On the Raspberry Pi port, all encoder lines need 3.3V supply and a voltage divider or logic-level converter on the output lines.

### 3.3 Button Wiring

```
Each button (×4 including half-nut lever):

  5V ──┐
       └── [Button] ──┬──── Arduino digital input pin
                      │
                   10kΩ
                      │
                     GND
```

Button pressed → pin reads HIGH. Button released → pin reads LOW (via pull-down). Software debounce is implemented in `01_Buttons.ino`.

### 3.4 Potentiometer Wiring

```
  5V ──── Pot end A
  GND ─── Pot end B
  Wiper ── A3 (Arduino analogue input)
```

Reads 0–1023 (10-bit ADC). Values below 18 clamp to minimum feed; above 1007 clamp to maximum feed.

### 3.5 Spindle Sensor (AutoTech C3 / Hall-effect)

```
  C3 output ──── D13 (Arduino digital input)
  C3 VCC    ──── 5–12V (per sensor spec)
  C3 GND    ──── GND
```

Connected via `enableInterrupt(13, spindRevCount, RISING)`. One pulse per spindle revolution. The interrupt fires `spindRevCount()` which timestamps the event using `micros()`.

---

## 4. Software Architecture

The sketch is split across 14 `.ino` files that Arduino IDE compiles as a single translation unit:

| File | Function(s) inside | Role |
|---|---|---|
| `Lathe_v0.5.25_alpha0.1.ino` | `setup()`, `loop()`, all global vars | Main file, variable declarations, init, main loop |
| `01_Buttons.ino` | `stdButtons()`, `modeButtons()`, `arcButtons()` | All button press/hold logic |
| `10_SpdFeed.ino` | `spindRevCount()`, `spindIndex()`, `calcSpeed()`, `potentiometer()`, `calcFeed()` | Spindle RPM and feed rate calculation |
| `20_HandWh_Z.ino` | `zEnc()` | Z-axis handwheel encoder → motor drive loop |
| `21_HandWh_X.ino` | `xEnc()` | X-axis handwheel encoder → motor drive loop |
| `30_HalfNut.ino` | `zMotorFeed()` | Electronic half-nut feed with auto-stop |
| `40_Thread.ino` | `extThrdSetup()`, `extThrdMove()`, helper sub-steps | External thread cutting wizard + motion |
| `50_Profile.ino` | `taperSetup()`, `tprMove()`, sub-steps | Profile / taper turning wizard + motion |
| `60_Radius.ino` | `arcSetup()`, `arcMove()`, sub-steps | Radius / sphere turning wizard + motion |
| `70_Mode.ino` | `modeSetup()` | Mode selection entry point (resets all mode variables) |
| `71_Pause.ino` | `pauseMode()` | Pause state handling |
| `81_LCD_Basic.ino` | `displayLcdBasicsXZ()`, `lcdFeedDispBasic()` | LCD static text and memory/unit labels |
| `82_LCD_Z.ino` | `displayLcdFullValZ()`, `displayLcdPartValZ()` | Z position LCD update (full and partial) |
| `83_LCD_X.ino` | `displayLcdFullValX()`, `displayLcdPartValX()` | X position LCD update |
| `84_LCD_SpFeed.ino` | `displayLcdSpeed()`, `displayLcdFeed()`, `displayLcdStop()` | RPM, feed rate, and Z-stop display |

### Main Loop

```
loop() {
    zEnc()          — check Z encoder, drive Z motor
    xEnc()          — check X encoder, drive X motor
    potentiometer() — read pot, recalculate feed rate
    spindIndex()    — check spindle RPM from timestamp
    zMotorFeed()    — check half-nut lever, run feed
    stdButtons()    — check 3 buttons (standard mode only)
    modeSetup()     — handle mode selection entry
    extThrdSetup()  — run threading wizard (if modeCt==1)
    taperSetup()    — run profile wizard (if modeCt==3)
    arcSetup()      — run radius wizard (if modeCt==4)
}
```

The loop runs continuously with no `delay()` calls in the main path. All timing is based on `micros()` and `millis()` delta calculations.

---

## 5. Function Descriptions

### 5.1 `zEnc()` — Z Handwheel Following

**File:** `20_HandWh_Z.ino`

Reads the Z-axis encoder position. If position has changed since the last call, it:

1. Accumulates the change into a floating-point buffer (`zEncBuffer`).
2. Calculates how many motor steps the buffer represents using the gear-ratio constant `zCountAdjust` (motor counts / encoder count).
3. Calculates the implied velocity from the buffer size.
4. Selects a step burst size and delay time matched to that velocity (5 velocity bands A–E).
5. Updates the Z display on the LCD.
6. Calls `Z.move(zStepSize)` to send the motor command.
7. Waits `delayMicroseconds(zDelay)` — this delay **is** the velocity control.
8. Loops until the buffer is drained.

If the motor doesn't complete its previous command in time, the LCD shows `ER: Z-Mtr`.

**Key constants:**

| Constant | Value | Meaning |
|---|---|---|
| `zCountAdjust` | 1.6 | Motor counts per encoder count |
| `zVelLimitA–E` | 20/100/800/2000 counts/s | Velocity band thresholds |
| `zMaxEncBuf` | 600 counts | Maximum encoder buffer before clamping |

### 5.2 `xEnc()` — X Handwheel Following

**File:** `21_HandWh_X.ino`

Identical logic to `zEnc()` but for the X axis. Uses separate variables and constants. The X axis has a smaller pitch (2.0 mm vs 5.0 mm) so `xCountAdjust` = 0.4 (motor counts per encoder count).

### 5.3 `zMotorFeed()` — Electronic Half-Nut Feed

**File:** `30_HalfNut.ino`

Called every loop iteration. Engages when the half-nut lever switch (`D8`) goes HIGH:

1. Saves current motor and encoder positions as `tempMtrPosZ`, `tempEncPosZ`.
2. Calculates step size from feed rate (mm/min) and minimum safe inter-step delay (600 µs).
3. Calculates a "pre-step" to align the move to an exact multiple of the step size at the stop point.
4. Calculates `halfnutMoveDist` — either the distance to the Z-stop, or `zMaxMtrCnt` if no stop is set.
5. Runs a `while(k>0)` loop:
   - Delays `zFeedDelay` microseconds.
   - Calls `Z.move(zFeedStep)` to issue the next step burst.
   - Checks if at target (`actualMoveNew >= halfnutMoveDist`) or lever disengaged.
   - Exits when either condition is true.
6. On completion: restores encoder count registers so the DRO position is correct.

**Auto-stop mechanism:** The function checks `memStopZ[mZ]` (set by Button 3 medium hold). When the carriage reaches that motor count, the while loop exits and the feed stops cleanly.

### 5.4 `spindRevCount()` and `spindIndex()` — Spindle RPM

**File:** `10_SpdFeed.ino`

`spindRevCount()` is an interrupt service routine (ISR) called on each rising edge from the spindle sensor. It timestamps each revolution using `micros()`.

`spindIndex()` (called in the main loop) computes:

$$RPM = \frac{1{,}000{,}000 \times 60}{\Delta t_{index}}$$

where $\Delta t_{index}$ is the time in microseconds between the last two index pulses. Updates are gated — RPM only updates if it changes by more than 2 RPM, or if within 2.5 seconds and changed by more than 3 RPM. This prevents display flickering.

### 5.5 `potentiometer()` and `calcFeed()` — Feed Rate Control

**File:** `10_SpdFeed.ino`

`potentiometer()` reads `analogRead(A3)` every loop and detects changes > 5 counts or > 1 count within 2.5 seconds.

`calcFeed()` maps the ADC value (0–1023) to a feed rate:

$$feedRateMm = \text{map}(potNew, 18, 1007, feedRateMin, feedRateMax)$$

- `feedRateMin` = 12.7 mm/min (0.5 IPM)
- `feedRateMax` = 1270.0 mm/min (50 IPM)
- `feedRate` (displayed) = `feedRateMm / 25.4` → always shown in IPM

### 5.6 `stdButtons()` — Standard Mode Button Handling

**File:** `01_Buttons.ino`

Handles 3 physical push-buttons with press-duration logic:

**Button 1 (D49) — X axis:**
| Duration | Action |
|---|---|
| < 600 ms | Cycle X memory slot: M1 → M2 → M3 → M1 |
| > 600 ms | Zero X: set `memOffsetX[mX] = mtrNewPosX` |

**Button 2 (D51) — Z axis:**
| Duration | Action |
|---|---|
| < 600 ms | Cycle Z memory slot; reset Z-stop display |
| > 600 ms | Zero Z: set `memOffsetZ[mZ] = mtrNewPosZ` |

**Button 3 (D50) — General:**
| Duration | Action |
|---|---|
| < 600 ms | Toggle display units: mm ↔ inch (`unitConverter` = 1.0 or 25.4) |
| 600–1800 ms | Set Z auto-stop: `memStopZ[mZ] = mtrNewPosZ` |
| 1800–5000 ms | Enter mode selection: `modeCt = 999` |
| ≥ 10,000 ms | Reset error display on LCD |

Debounce time: 40 ms (120 ms for Button 3).

### 5.7 `modeSetup()` — Mode Selection

**File:** `70_Mode.ino`

Entered when `modeCt == 999`. Displays `"Select Mode, B3:OK"` and lists available modes. In mode-select state, Button 1 / Button 2 cycle through modes, Button 3 accepts. All threading, profile, and arc variables are reset before entering a new mode.

Available modes:
| `modeCt` value | Mode |
|---|---|
| 0 | Standard (DRO + handwheel) |
| 1 | External Thread Cutting |
| 3 | Profile / Taper |
| 4 | Radius / Sphere |

### 5.8 `extThrdSetup()` — External Thread Cutting Wizard

**File:** `40_Thread.ino`

A sequential state machine controlled by `tQustCt` (question counter). The operator steps through each question using Button 3 to accept. Buttons 1 and 2 cycle selections.

**Wizard steps (`tQustCt` value):**

| Step | Question | What operator does |
|---|---|---|
| 0–1 | Thread size | Scroll through 18 sizes (UNC/UNF + metric) |
| 2–3 | Part material | Aluminum / Mild Steel / Stainless / Brass |
| 4–5 | Cutting tool | HSS or Carbide (Carbide forced if RPM too low for HSS) |
| 6–7 | Turn and measure OD | Machine OD to nominal, measure actual. B1/B2 adjust ±0.001 |
| 8–9 | Set C391 gauge | Touch Starrett C391 gauge to OD, accept position |
| 10–11 | Set tool tip | Touch threading cutter to OD, accept position |
| 12 | Calculate infeed | Wizard calculates total infeed, pass count, depth/pass |
| 13+ | Set X retract | Move X to clear diameter, accept |
| 15+ | Set Z end | Move Z to thread end, accept |
| 16+ | Set Z start | Move Z to thread start, accept |
| 30+ | Run pass | System drives: rapid to end, advance X by infeed, thread pass, retract X, return to start |

**Automatic RPM recommendation:**

$$RPM_{rec} = \frac{SFM \times 4}{OD_{nominal}(in)}$$

where SFM comes from the material table (Aluminum=200, Mild Steel=100, Stainless=60, Brass=200).

**Thread infeed calculation (modified flank):**

$$infeedTotal = \frac{\sqrt{2} \times pitch}{2} \times \tan(27.5°)$$

Each pass deepens by a calculated amount, with spring passes at the end.

### 5.9 `taperSetup()` — Profile / Taper Wizard

**File:** `50_Profile.ino`

Cuts a profile defined by up to 10 X/Z coordinate pairs. The wizard:

1. Touches tool to stock OD to calibrate X reference.
2. Operator sets X retract position (must be ≥ 1 mm from stock).
3. Selects number of profile points (2–10).
4. Operator positions tool at each point; wizard records X/Z coordinates.
5. Wizard calculates rough and finish pass depths, cut direction, pass count.
6. Executes passes: for each pass, traverses all point-segments with inter-segment linear interpolation in X and Z simultaneously.

### 5.10 `arcSetup()` — Radius / Sphere Wizard

**File:** `60_Radius.ino`

Cuts arcs and spheres. Two arc types:

- **Internal radius** — concave form (e.g. spherical concave)
- **External radius** — convex form (e.g. ball-nose, hemisphere)

The wizard collects:
- Arc type (internal/external)
- Insert type (round / diamond) and size
- Known OD position for X calibration
- Face position for Z centre calibration
- Desired arc radius
- OD tangent position (for external — where arc meets the OD)
- Face extension (for "dumbbell" forms)

Then executes a series of passes interpolating simultaneously in X and Z to approximate the arc using many small linear segments (8-point lookup tables `arcX[]`, `arcZ[]`).

---

## 6. Motor Drive Signal Chain

### How a motor command travels from handwheel to servo

```
 Operator turns handwheel
         │
         ▼
 Encoder (CUI AMT103-V) — 2000 CPR quadrature
         │ interrupt pins, Encoder.h library
         ▼
 zAxisEnc.read() → encoder count delta
         │
         ▼
 zEncBuffer += delta    (floating-point accumulator)
         │
         ▼
 while(buffer ≥ threshold):
   calculates zStepSize and zDelay
         │
         ▼
 PulseClearpath::move(zStepSize)
   sets DIR pin HIGH/LOW
   loads _commandX = |zStepSize|
         │  (returns immediately)
         ▼
 StepController ISR (Timer2 @ 2 kHz)
   calls calcSteps() → burst of ≤50 pulses
   writes directly to PORTA (D22–D29)
   sets STEP HIGH → delayMicroseconds(2) → STEP LOW
         │
         ▼
 ClearPath SDSK servo
   counts pulses, controls internal PID loop
   drives motor shaft to commanded position
         │
         ▼
 Leadscrew rotates → carriage moves
```

### Step/Direction signal specification

| Signal | Level | Arduino pin | ClearPath input |
|---|---|---|---|
| DIR (Z) | 5V TTL HIGH/LOW | D22 | A pin |
| STEP (Z) | 5V TTL pulse, 2 µs HIGH | D23 | B pin |
| ENABLE (Z) | Active LOW to enable | D27 | E pin |
| DIR (X) | 5V TTL HIGH/LOW | D24 | A pin |
| STEP (X) | 5V TTL pulse, 2 µs HIGH | D25 | B pin |
| ENABLE (X) | Active LOW to enable | D26 | E pin |

---

## 7. Position Tracking and Memory System

The system tracks position in **motor counts** (absolute from power-on = 0):

- `mtrNewPosZ` — absolute Z motor count (signed long)
- `mtrNewPosX` — absolute X motor count (signed long)

**Display conversion:**

$$position_{mm} = -\frac{(mtrNewPos - memOffset[slot]) \times pitch}{countsPerRev}$$

The negative sign corrects for the convention that the carriage moving toward the chuck decreases the displayed Z value (matches lathe convention: Z positive = away from chuck).

**Memory slots:**

```
memOffsetZ[0]  = M1 zero reference (motor counts)
memOffsetZ[1]  = M2 zero reference
memOffsetZ[2]  = M3 zero reference
active slot = mZ (0, 1, or 2)
```

Zeroing (`Button 1/2 long hold`) sets `memOffsetZ[mZ] = mtrNewPosZ`, so the display reads 0.000.

**Z auto-stop:**

```
memStopZ[0]  = M1 stop position (motor count, or 999999 = not set)
memStopZ[1]  = M2 stop position
memStopZ[2]  = M3 stop position
```

Each memory slot has its own stop position. The stop is displayed relative to the memory's zero using the same offset conversion.

---

## 8. LCD Display Layout

The 4×20 character LCD always shows:

```
Row 0: X =  +00.0000 in  M1
Row 1: Z =  +000.000 mm  M3
Row 2: RPM = 0000    Z-STOP
Row 3: IPM = 00.0   -123.456
```

- Position values: 7 characters wide, right-aligned with sign. `mm`: 3 decimal places. `in`: 4 decimal places.
- `M1/M2/M3`: active memory slot, column 19.
- `RPM`: columns 6–9 of row 2, 4-digit integer.
- `IPM`: columns 6–9 of row 3, 4.1 format.
- `Z-STOP`: either `Not Set`, `±xxx.xxx`, or `+++>>>` (apron past stop).

**LCD update strategy:** To keep up with fast handwheel motion (LCD writes take 3,500–8,500 µs), the update is split into partial writes that alternate each motor step. Only changed characters are written, using cursor positioning.

---

## 9. Key Constants (User Configurable)

These are defined at the top of the main `.ino` file and must be set to match the specific lathe:

| Constant | Default | Description |
|---|---|---|
| `zMtrPulley` | 28 | Teeth on Z motor pulley |
| `zScrPulley` | 28 | Teeth on Z leadscrew pulley |
| `zScrPitch` | 5.0 mm | Z leadscrew pitch |
| `zHandwheel` | 20.0 mm/rev | Linear travel per Z handwheel revolution |
| `zEncCntPerRev` | 2000 | Z encoder counts per revolution |
| `zMtrCntPerRev` | 800 | Z motor counts per revolution (set in ClearPath MSP) |
| `xMtrPulley` | 24 | Teeth on X motor pulley |
| `xScrPulley` | 24 | Teeth on X leadscrew pulley |
| `xScrPitch` | 2.0 mm | X leadscrew pitch |
| `xHandwheel` | 2.0 mm/rev | Linear travel per X handwheel revolution |
| `xEncCntPerRev` | 2000 | X encoder counts per revolution |
| `xMtrCntPerRev` | 800 | X motor counts per revolution |
| `spndlRpmMax` | 2060 RPM | Machine spindle maximum |
| `spndlRpmMin` | 240 RPM | Machine spindle minimum |
| `feedRateMin` | 12.7 mm/min | Minimum electronic feed (0.5 IPM) |
| `feedRateMax` | 1270 mm/min | Maximum electronic feed (50 IPM) |
| `zMaxTravel` | 1000 mm | Maximum Z travel range |
| `mtrMinDelay` | 600 µs | Minimum inter-step delay (servo limit) |
| `thrdC391` | 13.860 mm | Starrett C391 gauge dimension (must be measured) |
| `thrdAng` | 27.5° | Modified flank infeed angle |

---

## 10. Libraries Used

| Library | Purpose | Source |
|---|---|---|
| `Encoder.h` | Quadrature encoder reading (interrupt-driven) | Paul Stoffregen — github.com/PaulStoffregen/Encoder |
| `PulseClearpath.h` | ClearPath motor step/direction command interface | Rob Wade — wadeodesign.com |
| `StepController.h` | Timer2 ISR pulse generation (2 kHz) | Rob Wade — wadeodesign.com |
| `Wire.h` | I2C communication for LCD | Arduino standard library |
| `LiquidCrystal_I2C.h` | I2C LCD driver | fdebrabander — github.com |
| `EnableInterrupt.h` | Flexible interrupt assignment (spindle on D13) | GreyGnome — github.com |

---

## 11. Operating Modes Summary

| Mode | `modeCt` | Entry | What it does |
|---|---|---|---|
| Standard DRO | 0 | Power-on default | Handwheel following, half-nut feed, all buttons active |
| Thread Cutting | 1 | Mode select → Thread | Guided thread setup wizard + automated pass execution |
| Profile/Taper | 3 | Mode select → Profile | Multi-point contour wizard + automatic multi-pass execution |
| Radius/Sphere | 4 | Mode select → Radius | Arc-type selection wizard + arc interpolation passes |
| Mode Select | 999 | Button 3 long hold | Transition state before entering a working mode |

---

## 12. Known Limitations of the Arduino Version

| Limitation | Note |
|---|---|
| **Single core, no pre-emption** | All tasks share one CPU core. LCD updates compete with motor timing. At high speeds the display drops to partial updates (see velocity bands). |
| **Integer overflow** | Position tracking uses `long` (32-bit). At 800 counts/rev over 1000 mm / 5 mm pitch = 160,000 counts max. Well within 32-bit range, but not validated for longer beds. |
| **No limit switches** | The original Arduino design has no hardware limit switch inputs. The Raspberry Pi port adds 4 limit switch inputs with auto-stop and back-off logic. |
| **No internal threading** | Only external (OD) thread cutting is implemented. The mode list includes "Internal Thread" (modeCt = 2) but the code is not implemented. |
| **No persistent storage** | Memory offsets (M1/M2/M3) and stops are reset every power cycle. EEPROM storage was planned (`TODO` comments in code) but not implemented. |
| **C391 tool required** | The threading wizard requires a Starrett C391 gauge tool to set the X datum. Using a thread-cutting insert directly requires manually entering the equivalent dimension. |

---

*Document generated from source analysis of Lathe_v0.5.25_alpha0.1 by Rob Wade.*  
*Last updated: 31 March 2026*
