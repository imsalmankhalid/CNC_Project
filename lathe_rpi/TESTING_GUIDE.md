# MbW Lathe – Operating & Manual Testing Guide

This guide explains how to **start**, **operate**, **close**, and **manually
test** the lathe control application on the Raspberry Pi 5. No prior knowledge
of the UI is assumed.

---

## 1. Starting the application

You have three ways to launch it:

| Method | How |
|---|---|
| **Desktop icon** | Double-click **“MbW Lathe”** on the Desktop (installed by `install_desktop.sh`). |
| **Applications menu** | Find **MbW Lathe** under *Utility / Engineering*. |
| **Terminal** | `cd ~/CNC_Project/lathe_rpi && ./run_lathe.sh` |

### Debug mode (turns on detailed logs)
For hardware testing, launch with logging turned up:

```bash
./run_lathe.sh --debug
```

This sets `LATHE_DEBUG_HAL=1`, which logs every encoder / pot / step / button
event. (You can also install a separate debug desktop icon with
`./install_desktop.sh --debug`.)

> The Wayland warnings you may see at startup
> (`QStandardPaths: wrong permissions…`, `Wayland does not support
> QWindow::requestActivate()`, `GLib-GObject-CRITICAL`) are **harmless** – they
> come from Qt running under Wayland and do not affect operation.

---

## 2. Closing the application

On a fullscreen touchscreen there is now more than one way out:

- **✕ EXIT** button (bottom bar, next to E‑STOP) → asks for confirmation, then quits.
- **Ctrl + Q** on an attached keyboard → quits immediately.
- **F11** → toggles fullscreen ↔ windowed (handy when testing on a monitor).

If it ever gets stuck, from a terminal: `pkill -f main.py`.

---

## 3. Reading the main screen (DRO)

```
┌───────────────────────────────────────────────────────────┐
│  X   +0.0000 mm  M1  │  RPM  0000  │  Z-STOP  Not Set       │
│  ─────────────────── │  ───────── │  LIMITS                 │
│  Z   +0.000  mm  M1  │  IPM  00.0  │  ◉Z+ ◉Z- ◉X+ ◉X-       │
├───────────────────────────────────────────────────────────┤
│ X M1▶ ZERO X  Z M1▶ ZERO Z  mm/in  SET STOP  CLR STOP  MODES▶  ✕EXIT  ⬛E-STOP │
└───────────────────────────────────────────────────────────┘
```

- **X / Z values** – the digital read‑out (DRO) position of each axis. These
  move when you turn the corresponding handwheel/encoder.
- **M1 / M2 / M3** – the active memory slot (independent zero offset) per axis.
- **RPM** – spindle speed (from the spindle index sensor).
- **IPM** – feed rate set by the potentiometer.
- **Z‑STOP** – the Z auto‑stop target (`Not Set` until you set one).
- **LIMITS** – four dots; a dot turns to a red square ⬛ when that limit switch
  is triggered.

### Bottom bar buttons

| Button | Action |
|---|---|
| **X M1▶** | Cycle the X memory slot (M1→M2→M3). |
| **ZERO X** | Zero the X axis at the current position (in the active slot). |
| **Z M1▶** | Cycle the Z memory slot. |
| **ZERO Z** | Zero the Z axis at the current position. |
| **mm / in** | Toggle display units (mm ↔ inch). |
| **SET STOP** | Set the Z auto‑stop to the current Z position. |
| **CLR STOP** | Clear the Z auto‑stop. |
| **MODES▶** | Open the mode selection screen. |
| **✕ EXIT** | Quit the app (with confirmation). |
| **⬛ E‑STOP** | Toggle emergency stop. When active it turns red and blocks motion; press again (**RESET ESTOP**) to clear. |

### Physical panel buttons (if wired)
The three hardware buttons behave like the Arduino version (short vs. long press):

| Button | Short press | Long press |
|---|---|---|
| **1** | Cycle X memory | Zero X |
| **2** | Cycle Z memory | Zero Z |
| **3** | Toggle mm/inch | Long → open Modes; medium → set Z‑stop |

---

## 4. Mode navigation

Tap **MODES▶** to open the mode grid:

- **DRO / Handwheel** – normal operation (this is the default screen).
- **Thread Cutting**
- **Profile / Taper**
- **Radius / Sphere**

Each mode screen has an **exit/back** control that returns you to the main DRO
screen. Handwheel motion is only processed in DRO, Profile and Radius modes.

---

## 5. Manual hardware test procedure

Do these one at a time. Launch in debug mode first:

```bash
./run_lathe.sh --debug
```

Keep the terminal visible **and** watch the screen. Logs also stream to
`logs/lathe.log` (see §6).

### 5.1 Encoders (handwheels)
1. Slowly turn the **X handwheel**.
2. **Expect:** the on‑screen **X** value changes, and the log shows lines like
   `X encoder = 1234 (+8)` and `X handwheel: enc … -> … (delta +8)`.
3. Repeat with the **Z handwheel** → the **Z** value should change and log
   `Z encoder = …`.

> If an axis shows `… (idle)` with a constant number while you turn it, the
> encoder counts are not reaching the app → check that encoder’s wiring/pins
> (Z = GPIO 5/6, X = GPIO 13/19).

### 5.2 Direction check
- Turning a handwheel one way should increase the value, the other way should
  decrease it. If a motor drives the **wrong direction**, that axis’s DIR line
  needs inverting.

### 5.3 Potentiometer (feed rate)
1. Turn the feed potentiometer.
2. **Expect:** the **IPM** value changes, and the log shows
   `pot 1.234V -> 512/1023`.
3. Fully down ≈ minimum feed, fully up ≈ maximum feed.

### 5.4 Buttons
- Press each panel button and confirm the matching action on screen (memory
  cycles, zero, unit toggle). Debug logs also record button activity.

### 5.5 Half‑nut switch
- Engage/disengage the half‑nut lever; in threading mode this gates the
  synchronized feed.

### 5.6 Limit switches
1. Trigger each limit switch by hand.
2. **Expect:** the matching **LIMITS** dot turns into a red square ⬛.
3. With a limit active, motion in that direction is blocked.

### 5.7 Spindle sensor (RPM)
1. Rotate the spindle (or pulse the index sensor).
2. **Expect:** the **RPM** value updates; debug log shows
   `spindle index pulse`.

### 5.8 Motors / E‑STOP
1. Press **⬛ E‑STOP** → it turns red; handwheel motion should no longer drive
   the motors.
2. Press again to reset, and confirm motion resumes.

---

## 6. Reading the logs

Logs go to **both** the console and a rotating file, controlled in `config.py`:

| Setting | Meaning |
|---|---|
| `LOG_TO_CONSOLE` | show logs in the terminal |
| `LOG_TO_FILE` | write logs to `LOG_FILE` |
| `LOG_FILE` | default `logs/lathe.log` |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

To watch the log live in another terminal:

```bash
tail -f ~/CNC_Project/lathe_rpi/logs/lathe.log
```

After a test session, the file `logs/lathe.log` contains the full trace – share
it (or ask me to read it) to diagnose issues.

---

## 7. Low‑level bench test (no UI)

To test motors + encoders + pot directly, without the GUI, use the validated
hardware script:

```bash
cd ~/CNC_Project/lathe_rpi/test
../env/bin/python enc_drive_motor.py
```

This is an electronic‑gearbox demo: turning each encoder drives its motor, and
the potentiometer sets the gear ratio. It prints a live status line. Press
**Ctrl+C** to stop. Use this to confirm wiring before running the full app.

---

## 8. Quick troubleshooting

| Symptom | Check |
|---|---|
| An axis value never moves | Turn it in `--debug`; if the encoder log stays `(idle)`, it’s wiring/pins for that encoder. |
| Motor runs backwards | Invert that axis’s DIR line (or swap in config). |
| No RPM | Spindle index sensor wiring / `spindle index pulse` log absent. |
| No feed change | Potentiometer / ADS1015 on I²C; check `pot … -> …` log. |
| Buttons overlap / can’t exit | Fixed – bottom bar is sized for the E‑STOP button and an **✕ EXIT** button + **Ctrl+Q** are provided. |
| App won’t close | **✕ EXIT**, **Ctrl+Q**, or `pkill -f main.py`. |
