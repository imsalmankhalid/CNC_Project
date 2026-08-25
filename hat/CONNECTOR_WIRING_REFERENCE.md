# MbW Lathe HAT – Connector Wiring Quick Reference Card
**Print this for workshop use during wiring and assembly**

---

## 🔌 J1 – Raspberry Pi GPIO (40-pin)
```
DO NOT WIRE – This is the HAT-to-RPi connector (socket)
Plugs directly onto Raspberry Pi GPIO header
```

---

## ⚙️ J2 – X-Axis Motor (ClearPath SDSK)
**6-pin Terminal Block**
```
┌─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │
│ ST  │ DR  │ EN  │ GND │ +5V │ HF  │
└─────┴─────┴─────┴─────┴─────┴─────┘

Pin 1: X_STEP    → ClearPath STEP input (5V TTL)
Pin 2: X_DIR     → ClearPath DIR input (5V TTL)
Pin 3: X_ENABLE  → ClearPath ENABLE input (5V TTL, active HIGH)
Pin 4: GND       → ClearPath signal ground
Pin 5: +5V       → ClearPath logic power (NOT motor power)
Pin 6: HLFB      → Hardware feedback (leave unconnected if not used)

⚠️ Motor high voltage (70V) is supplied EXTERNALLY, not through this connector.
```

---

## ⚙️ J3 – Z-Axis Motor (ClearPath SDSK)
**6-pin Terminal Block**
```
┌─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │
│ ST  │ DR  │ EN  │ GND │ +5V │ HF  │
└─────┴─────┴─────┴─────┴─────┴─────┘

Pin 1: Z_STEP    → ClearPath STEP input (5V TTL)
Pin 2: Z_DIR     → ClearPath DIR input (5V TTL)
Pin 3: Z_ENABLE  → ClearPath ENABLE input (5V TTL, active HIGH)
Pin 4: GND       → ClearPath signal ground
Pin 5: +5V       → ClearPath logic power
Pin 6: HLFB      → Hardware feedback (leave unconnected if not used)

⚠️ Motor high voltage (70V) is supplied EXTERNALLY, not through this connector.
```

---

## 🔄 J4 – X-Axis Encoder (CUI AMT103-V)
**4-pin Terminal Block**
```
┌───────┬───────┬───────┬───────┐
│   1   │   2   │   3   │   4   │
│ +3V3  │  GND  │   A   │   B   │
└───────┴───────┴───────┴───────┘

Pin 1: +3.3V  → Encoder power (3.3V rail)
Pin 2: GND    → Ground
Pin 3: A      → Quadrature A output
Pin 4: B      → Quadrature B output

🔌 External Encoder Wiring (AMT103-V):
   Pin 1 (VCC) → J4 Pin 1 (+3.3V)
   Pin 2 (GND) → J4 Pin 2 (GND)
   Pin 5 (A)   → J4 Pin 3
   Pin 6 (B)   → J4 Pin 4
   INDEX output not used
```

---

## 🔄 J5 – Z-Axis Encoder (CUI AMT103-V)
**4-pin Terminal Block**
```
┌───────┬───────┬───────┬───────┐
│   1   │   2   │   3   │   4   │
│ +3V3  │  GND  │   A   │   B   │
└───────┴───────┴───────┴───────┘

Pin 1: +3.3V  → Encoder power (3.3V rail)
Pin 2: GND    → Ground
Pin 3: A      → Quadrature A output
Pin 4: B      → Quadrature B output

🔌 External Encoder Wiring (AMT103-V):
   Pin 1 (VCC) → J5 Pin 1 (+3.3V)
   Pin 2 (GND) → J5 Pin 2 (GND)
   Pin 5 (A)   → J5 Pin 3
   Pin 6 (B)   → J5 Pin 4
   INDEX output not used
```

---

## 🎚️ J6 – Potentiometer (Feed Rate Control)
**3-pin Terminal Block**
```
┌───────┬────────┬───────┐
│   1   │   2    │   3   │
│  +5V  │ WIPER  │  GND  │
└───────┴────────┴───────┘

Pin 1: +5V    → Pot rail A (one end of resistive track)
Pin 2: WIPER  → Pot center tap (variable output)
Pin 3: GND    → Pot rail B (other end of resistive track)

🔌 External Pot Wiring (10kΩ linear):
   End A (pin 1 or 3) → J6 Pin 1 (+5V)
   Wiper (pin 2)      → J6 Pin 2
   End B (pin 3 or 1) → J6 Pin 3 (GND)

📝 Pot reads 0 when wiper is at GND end, 1023 when at +5V end.
```

---

## 🛑 J7 – Limit Switches (4× NO switches)
**8-pin Terminal Block**
```
┌──────┬─────┬──────┬─────┬──────┬─────┬──────┬─────┐
│  1   │  2  │  3   │  4  │  5   │  6  │  7   │  8  │
│ Z+   │ GND │ Z−   │ GND │ X+   │ GND │ X−   │ GND │
└──────┴─────┴──────┴─────┴──────┴─────┴──────┴─────┘

Pin 1: LIM_Z+   → Z-axis positive limit switch
Pin 2: GND      → Common ground
Pin 3: LIM_Z−   → Z-axis negative limit switch
Pin 4: GND      → Common ground
Pin 5: LIM_X+   → X-axis positive limit switch
Pin 6: GND      → Common ground
Pin 7: LIM_X−   → X-axis negative limit switch
Pin 8: GND      → Common ground

🔌 Switch Wiring (Normally-Open contact):
   Each switch: One terminal to signal pin (1/3/5/7)
                Other terminal to adjacent GND pin (2/4/6/8)
   Switch CLOSES (to GND) when limit is HIT → GPIO reads LOW
   Switch OPEN when not hit → GPIO reads HIGH (via pull-up)

⚠️ Hardware installed: Only 2 switches (Z+ on GPIO 16, X+ on GPIO 8)
   Z− and X− are reserved for future expansion.
```

---

## 🔘 J8 – Push Buttons (3× momentary)
**6-pin Terminal Block**
```
┌──────┬─────┬──────┬─────┬──────┬─────┐
│  1   │  2  │  3   │  4  │  5   │  6  │
│ BTN1 │ GND │ BTN2 │ GND │ BTN3 │ GND │
└──────┴─────┴──────┴─────┴──────┴─────┘

Pin 1: BTN1  → Push button 1 (GPIO 26)
Pin 2: GND   → Common ground
Pin 3: BTN2  → Push button 2 (GPIO 20)
Pin 4: GND   → Common ground
Pin 5: BTN3  → Push button 3 (GPIO 21)
Pin 6: GND   → Common ground

🔌 Switch Wiring (Normally-Open momentary):
   Each button: One terminal to signal pin (1/3/5)
                Other terminal to adjacent GND pin (2/4/6)
   Button pressed → GPIO reads LOW
   Button released → GPIO reads HIGH (via pull-up)

📝 Button functions (configured in software):
   BTN1: Memory store / Zero
   BTN2: Units toggle (mm / inch)
   BTN3: Mode select (context-dependent)
```

---

## 🔌 J9 – 12V DC Power Input
**5.5mm × 2.1mm Barrel Jack (Center-Positive)**
```
   ╔═══╗
   ║ + ║  Center pin: +12V DC
   ╠═══╣
   ║ − ║  Sleeve: GND
   ╚═══╝

⚠️ POLARITY: Center-positive (standard)
⚡ Voltage: 12V DC, regulated
📊 Current: 1A minimum (2A recommended)
🔌 Connector: 5.5mm outer diameter, 2.1mm inner diameter

✅ Compatible PSU: Standard 12V "wall wart" power adapter
❌ DO NOT use laptop PSU (usually 19-20V) – will damage board!
```

---

## 🔧 J10 – Half-Nut Switch
**2-pin Terminal Block**
```
┌─────────┬─────┐
│    1    │  2  │
│ HALF-NUT│ GND │
└─────────┴─────┘

Pin 1: HALF_NUT  → Half-nut lever switch (GPIO 4)
Pin 2: GND       → Common ground

🔌 Switch Wiring (SPST, Normally-Open):
   One terminal → J10 Pin 1
   Other terminal → J10 Pin 2 (GND)
   
   Switch CLOSED (engaged) → GPIO 4 reads HIGH (via pull-down to +3.3V)
   Switch OPEN (disengaged) → GPIO 4 reads LOW (pulled to GND)

⚠️ Alternative wiring (if using NO switch to GND + pull-up):
   Check config.py for active logic level.
```

---

## 🌀 J11 – Spindle Index Sensor (AutoTech C3)
**3-pin JST-PH 2.0mm or Terminal Block**
```
┌──────┬─────┬────────┐
│  1   │  2  │   3    │
│ +5V  │ GND │ SIGNAL │
└──────┴─────┴────────┘

Pin 1: +5V     → Sensor power (from 5V rail)
Pin 2: GND     → Common ground
Pin 3: SIGNAL  → 5V TTL pulse (one pulse per spindle revolution)

🔌 External Sensor Wiring (AutoTech C3 Optical Index):
   C3 +5V  → J11 Pin 1
   C3 GND  → J11 Pin 2
   C3 OUT  → J11 Pin 3

📝 Signal is 5V TTL. HAT has voltage divider to 3.3V for RPi GPIO.
⚠️ Sensor must be powered from 5V (not 3.3V).
```

---

## 📐 Wire Gauge Recommendations

| Connection | Wire Gauge | Notes |
|------------|------------|-------|
| **12V Power (J9)** | 18 AWG (1 mm²) | Low voltage but moderate current |
| **Motor Signals (J2, J3)** | 22-24 AWG (0.5 mm²) | Signal only, not motor power |
| **Encoders (J4, J5)** | 24-26 AWG (0.25 mm²) | Low current, keep short |
| **Buttons/Limits (J7, J8)** | 22-24 AWG (0.5 mm²) | Standard hookup wire |
| **Potentiometer (J6)** | 24-26 AWG (0.25 mm²) | Analog signal, shielded cable recommended |
| **Spindle Index (J11)** | 24 AWG (0.5 mm²) | 5V signal, moderate length OK |

---

## 🧪 Testing Procedure (After Wiring)

### 1. Visual Inspection
- [ ] All connectors firmly seated
- [ ] No loose strands shorting adjacent terminals
- [ ] Polarity correct on J9 (12V)
- [ ] Encoder and motor connectors not swapped

### 2. Power-On Test (No RPi)
- [ ] Connect 12V to J9
- [ ] Check for smoke/heat
- [ ] Measure 5V at J2 Pin 5 (should be 4.8-5.2V)

### 3. RPi Connection Test
- [ ] Mount HAT on Raspberry Pi
- [ ] Power RPi via USB-C
- [ ] Run `i2cdetect -y 1` → should see device at 0x48 (ADS1115)

### 4. Encoder Test
- [ ] Run `lathe_rpi/test/gpio_test.py`
- [ ] Rotate X encoder → verify count changes
- [ ] Rotate Z encoder → verify count changes

### 5. Motor Test (⚠️ CAUTION: Motors will move)
- [ ] Verify encoder connections correct
- [ ] Apply 70V motor power
- [ ] Run `lathe_rpi/test/enc_drive_motor.py`
- [ ] Turn handwheel → motor should follow

---

## 🔧 Troubleshooting

| Symptom | Possible Cause | Fix |
|---------|---------------|------|
| No 5V on J2/J3 Pin 5 | 12V not connected, or regulator failure | Check J9, check MP2307/L7805 |
| Encoder not reading | Wrong pins, or 5V instead of 3.3V | Verify J4/J5 wiring, check power |
| Motor not moving | STEP/DIR swapped, or 70V power off | Check J2/J3 wiring, verify 70V PSU |
| Pot reads 0 always | Wiper not connected, or wrong pin | Check J6 Pin 2 continuity |
| Limit always triggered | NC switch used with NO config | Check config.py `LIMIT_NORMALLY_CLOSED` |
| RPM not reading | Spindle sensor unpowered, or wrong voltage | Check J11 +5V, verify voltage divider |

---

## 📞 Support References

- Full design document: [HAT_VERIFICATION_AND_LABELING_GUIDE.md](HAT_VERIFICATION_AND_LABELING_GUIDE.md)
- Hardware specifications: [lathe_rpi/HARDWARE.md](../lathe_rpi/HARDWARE.md)
- GPIO configuration: [lathe_rpi/config.py](../lathe_rpi/config.py)
- Connection guide: [lathe_rpi/PCB_Connections_Guide_v2.md](../lathe_rpi/PCB_Connections_Guide_v2.md)

---

**PRINT THIS SHEET AND KEEP IN WORKSHOP** 📋
