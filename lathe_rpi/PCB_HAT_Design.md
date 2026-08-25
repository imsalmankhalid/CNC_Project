# MbW Lathe System – Raspberry Pi HAT PCB Design Document

## Overview

This document specifies a custom PCB designed as a Raspberry Pi HAT (Hardware Attached on Top) that consolidates all signal conditioning, level shifting, ADC, and I/O connectivity for the MbW (Machine-by-Wire) lathe control system.

**Design goal:** A single PCB that plugs onto the Raspberry Pi 40-pin GPIO header and provides all necessary connectors for encoders, servo motors, buttons, limit switches, spindle sensor, and potentiometer — with onboard level shifters, ADC, and signal conditioning.

**What is NOT on the HAT:** 70V motor power supply (supplied directly to ClearPath servo motors externally).

---

## 1. Mechanical Specifications

| Parameter | Value |
|-----------|-------|
| **Form factor** | Standard Raspberry Pi HAT |
| **PCB dimensions** | 65.0 mm × 56.5 mm (standard HAT size) or slightly larger if needed |
| **Mounting** | 4× M2.5 standoffs (standard HAT mounting holes) |
| **GPIO header** | 2× 20-pin male header (standard 2.54 mm pitch) |
| **Stack height** | Max ~30 mm (including connectors) |

### HAT ID EEPROM (Optional but Recommended)
- AT24C32 on I2C (0x50) for HAT identification
- VCC_EEPROM from RPi 5V pin

---

## 2. Component Bill of Materials (BOM)

### 2.1 Level Shifters

| Qty | Part | Function | Notes |
|-----|------|----------|-------|
| 1 | TXB0108PW (TSSOP-20) or TXS0108E | 8-channel bidirectional level shifter (3.3V ↔ 5V) | Single chip handles all 6 STEP/DIR/ENABLE lines + 2 spare channels. VCCA=3.3V, VCCB=5V |

**Channel assignment on TXB0108:**
| AI/O | BI/O | Signal |
|------|------|--------|
| A1 | B1 | Z STEP |
| A2 | B2 | Z DIR |
| A3 | B3 | Z ENABLE |
| A4 | B4 | X STEP |
| A5 | B5 | X DIR |
| A6 | B6 | X ENABLE |
| A7 | B7 | (spare) |
| A8 | B8 | (spare) |

### 2.2 ADC

| Qty | Part | Function | Notes |
|-----|------|----------|-------|
| 1 | ADS1015IDGSR (SOIC-16) | 4-channel 12-bit ADC, I2C interface | 3.3V compatible. SDA/SCL to RPi I2C bus (GPIO 2/3). Channel A0 for potentiometer |

### 2.3 Voltage Divider (Spindle Index)

| Qty | Part | Function |
|-----|------|----------|
| 1 | 10 kΩ 0805 resistor | R1, top of divider |
| 1 | 20 kΩ 0805 resistor | R2, bottom of divider |

Divides 5V TTL spindle index pulse to ~3.3V for RPi GPIO 12.

### 2.4 Pull-up / Pull-down Resistors

| Qty | Part | Function |
|-----|------|----------|
| 6 | 10 kΩ 0805 | Button pull-up resistors (GPIO 26, 20, 21 + half-nut + 2 spare) |
| 4 | 10 kΩ 0805 | Limit switch pull-up resistors (GPIO 16, 7, 8, 11) |
| 2 | 4.7 kΩ 0805 | I2C bus pull-ups (SDA/SCL) — may be optional if ADS1015 has internal pull-ups |
| 2 | 10 kΩ 0805 | Encoder pull-ups (if needed for AMT103-V) |

### 2.5 Decoupling Capacitors

| Qty | Part | Function |
|-----|------|----------|
| 4 | 100 nF 0805 ceramic | Per IC power pin (TXB0108, ADS1015 × 2) |
| 2 | 10 µF 0805 ceramic | Bulk decoupling on 3.3V and 5V rails |

### 2.6 Protection Components

| Qty | Part | Function |
|-----|------|----------|
| 6 | TVS diode (e.g., PESD5V0S1UL) | ESD protection on motor signal lines |
| 1 | TVS diode | ESD protection on spindle index |
| 2 | 100 Ω 0805 current-limiting resistors | On STEP output lines (signal integrity) |
| 1 | PTC resettable fuse 500 mA | On 5V rail from RPi |

### 2.7 Connectors

| Qty | Part | Function | Pinout |
|-----|------|----------|--------|
| 2 | 6-pin JST PH 2.0 mm | Encoder connectors (AMT103-V) | VCC, GND, A, B, INDEX, (NC) |
| 2 | 8-pin Molex Mini-fit Jr. (or equivalent) | ClearPath servo signal connectors | STEP, DIR, ENABLE, HLFB, GND, 5V, (HV+, HV− pass-through not on board) |
| 1 | 3-pin JST PH 2.0 mm | Spindle index sensor | VCC (5V), GND, SIGNAL |
| 4 | 2-pin screw terminal 3.5 mm | Limit switches (Z+, Z−, X+, X−) | Signal, GND |
| 4 | 2-pin screw terminal 3.5 mm | Push buttons (BTN1, BTN2, BTN3, Half-Nut) | Signal, GND |
| 1 | 3-pin JST PH 2.0 mm | Potentiometer | VCC (5V), Wiper (to ADC), GND |
| 1 | 4-pin screw terminal 3.5 mm | E-Stop | NC contact, NO contact, COM, GND |
| 1 | 2×20 pin male header | Raspberry Pi GPIO (standard HAT) | Standard 40-pin GPIO |
| 1 | 2×20 pin female header | GPIO stack-through (for chaining) | Standard 40-pin GPIO |

### 2.8 Status LEDs

| Qty | Part | Function |
|-----|------|----------|
| 1 | Green LED + 330 Ω resistor | Power indicator (5V) |
| 1 | Red LED + 330 Ω resistor | E-Stop triggered |
| 1 | Yellow LED + 330 Ω resistor | Activity (blinks on step pulses) |

---

## 3. GPIO Pin Assignment (BCM Numbering)

All pins match the existing `config.py` assignments:

### Power & Ground (from RPi GPIO header)
| RPi Pin | Signal | Usage on HAT |
|---------|--------|-------------|
| Pin 1 | 3.3V | ADS1015 VDD, encoder VCC, level shifter VCCA |
| Pin 2 | 5V | Level shifter VCCB, button pulls, pot VCC, 5V for external sensors |
| Pin 6, 9, 14, 20, 25, 30, 34, 39 | GND | Common ground plane |

### Encoders (3.3V direct — no level shifting needed)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Z Encoder A | GPIO 5 | Pin 29 | Input | JST-6 (Z-ENC) pin 3 |
| Z Encoder B | GPIO 6 | Pin 31 | Input | JST-6 (Z-ENC) pin 4 |
| X Encoder A | GPIO 13 | Pin 33 | Input | JST-6 (X-ENC) pin 3 |
| X Encoder B | GPIO 19 | Pin 35 | Input | JST-6 (X-ENC) pin 4 |

### Spindle Index (via voltage divider)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Spindle Index | GPIO 12 | Pin 32 | Input | JST-3 (SPINDLE) pin 3 → voltage divider → GPIO |

### Servo Outputs (via TXB0108 level shifter: 3.3V → 5V)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Z STEP | GPIO 17 | Pin 11 | Output | GPIO → TXB0108 A1 → B1 → Molex-8 (Z-MOTOR) |
| Z DIR | GPIO 27 | Pin 13 | Output | GPIO → TXB0108 A2 → B2 → Molex-8 (Z-MOTOR) |
| Z ENABLE | GPIO 22 | Pin 15 | Output | GPIO → TXB0108 A3 → B3 → Molex-8 (Z-MOTOR) |
| X STEP | GPIO 24 | Pin 18 | Output | GPIO → TXB0108 A4 → B4 → Molex-8 (X-MOTOR) |
| X DIR | GPIO 23 | Pin 16 | Output | GPIO → TXB0108 A5 → B5 → Molex-8 (X-MOTOR) |
| X ENABLE | GPIO 25 | Pin 22 | Output | GPIO → TXB0108 A6 → B6 → Molex-8 (X-MOTOR) |

### Buttons (active LOW, internal or external pull-up)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Button 1 | GPIO 26 | Pin 37 | Input | Terminal (BTN1) |
| Button 2 | GPIO 20 | Pin 38 | Input | Terminal (BTN2) |
| Button 3 | GPIO 21 | Pin 40 | Input | Terminal (BTN3) |

### Half-Nut Switch (active HIGH, pull-down)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Half-Nut | GPIO 4 | Pin 7 | Input | Terminal (HALF-NUT) |

### Limit Switches (active LOW, pull-up)
| Signal | GPIO | RPi Pin | Direction | HAT Connector |
|--------|------|---------|-----------|---------------|
| Limit Z+ | GPIO 16 | Pin 36 | Input | Terminal (LIM Z+) |
| Limit Z− | GPIO 7 | Pin 26 | Input | Terminal (LIM Z−) |
| Limit X+ | GPIO 8 | Pin 24 | Input | Terminal (LIM X+) |
| Limit X− | GPIO 11 | Pin 23 | Input | Terminal (LIM X−) |

### I2C Bus (ADS1015)
| Signal | GPIO | RPi Pin | Direction | HAT Component |
|--------|------|---------|-----------|---------------|
| I2C SDA | GPIO 2 | Pin 3 | I2C | ADS1015 SDA + 4.7kΩ pull-up |
| I2C SCL | GPIO 3 | Pin 5 | I2C | ADS1015 SCL + 4.7kΩ pull-up |

### Unused GPIO Pins (pass-through only)
| RPi Pin | GPIO | Notes |
|---------|------|-------|
| Pin 10 | GPIO 12 (SPI MOSI) | Not used by lathe |
| Pin 21 | GPIO 9 (SPI CE1) | Not used |
| Pin 27 | GPIO 13 (SPI MISO) | Not used |
| Pin 28 | GPIO 14 (TXD) | Not used |
| Pin 29 | GPIO 15 (RXD) | Not used |
| Pin 32 | GPIO 12 | Spindle index (listed above) |

---

## 4. Schematic Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MbW LATHE HAT PCB                                │
│                                                                         │
│  ┌──────────────┐                                                       │
│  │  Raspberry   │  40-pin GPIO Header                                   │
│  │  Pi GPIO     │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                               │
│  ┌──────┴───────┐    ┌──────────────────┐                              │
│  │  Ground      │    │  TXB0108         │                              │
│  │  Plane       │    │  Level Shifter   │                              │
│  │  (3.3V + 5V) │    │  3.3V ↔ 5V      │                              │
│  └──────┬───────┘    └────────┬─────────┘                              │
│         │                     │                                        │
│         │    ┌────────────────┼────────────────┐                       │
│         │    │                │                │                       │
│         │    │                │                │                       │
│   ┌─────┴────┐  ┌────────────┴────┐  ┌────────┴────────┐              │
│   │ ADS1015  │  │  Voltage        │  │  Pull-up/        │              │
│   │ (I2C)    │  │  Divider        │  │  Pull-down       │              │
│   │          │  │  (Spindle)      │  │  Resistors       │              │
│   └─────┬────┘  └────────┬────────┘  └────────┬────────┘              │
│         │                │                    │                        │
│         │                │                    │                        │
│  ┌──────┴──────┐  ┌──────┴───────┐  ┌────────┴─────────┐              │
│  │ JST-3 Pot   │  │ JST-3       │  │ 4× 2-pin Term.   │              │
│  │ Connector   │  │ Spindle     │  │  (Limit Switches) │              │
│  └─────────────┘  │ Connector   │  └──────────────────┘              │
│                    └─────────────┘                                    │
│                                                                        │
│  ┌──────────────────┐   ┌──────────────────┐                          │
│  │ 2× JST-6         │   │ 4× 2-pin Term.   │                          │
│  │ (Encoders)       │   │  (Buttons +      │                          │
│  │                  │   │  Half-Nut)       │                          │
│  └──────────────────┘   └──────────────────┘                          │
│                                                                        │
│  ┌──────────────────────────────────────────────────┐                  │
│  │ 2× Molex-8 (ClearPath Servo Signals)             │                  │
│  │ Z-MOTOR: STEP, DIR, ENABLE, HLFB, GND, 5V       │                  │
│  │ X-MOTOR: STEP, DIR, ENABLE, HLFB, GND, 5V       │                  │
│  └──────────────────────────────────────────────────┘                  │
│                                                                        │
│  ┌──────────────────┐                                                  │
│  │ 4-pin Term.      │                                                  │
│  │ (E-Stop)         │                                                  │
│  └──────────────────┘                                                  │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Detailed Signal Flow

### 5.1 Encoder Signals (3.3V Direct)
```
AMT103-V Encoder ──→ JST-6 Connector ──→ [10kΩ pull-up] ──→ RPi GPIO
  Pin 1 (VCC)  ──→ 5V (on-board regulator or direct from RPi 5V)
  Pin 2 (GND)  ──→ GND plane
  Pin 5 (A)    ──→ GPIO 5 (Z) or GPIO 13 (X)
  Pin 6 (B)    ──→ GPIO 6 (Z) or GPIO 19 (X)
```
**Note:** AMT103-V outputs are open-drain with internal pull-up options. 3.3V compatible when powered from 3.3V. If powered from 5V, add a level shifter or voltage divider on A/B lines.

**Recommendation:** Power encoders from 3.3V rail for direct GPIO compatibility.

### 5.2 Servo STEP/DIR/ENABLE (3.3V → 5V Level Shifted)
```
RPi GPIO (3.3V) ──→ TXB0108 AI/O ──→ TXB0108 BI/O (5V) ──→ [100Ω] ──→ Molex-8 Connector ──→ ClearPath Motor
```

### 5.3 Spindle Index (5V → 3.3V Voltage Divider)
```
AutoTech C3 ──→ JST-3 Connector ──→ [10kΩ] ──┬── [20kΩ] ──→ GND
                                                │
                                              RPi GPIO 12
                                           (~3.33V at HIGH)
```

### 5.4 Potentiometer (via ADS1015)
```
Potentiometer ──→ JST-3 Connector
  VCC (5V) ──→ Pot end A
  GND    ──→ Pot end B
  Wiper  ──→ [10kΩ series] ──→ ADS1015 A0 ──→ I2C ──→ RPi GPIO 2/3
```

### 5.5 Buttons and Limit Switches
```
Button / Limit Switch ──→ Screw Terminal ──→ [pull-up 10kΩ] ──→ RPi GPIO
                                                    │
                                                  GND (switch closes to GND)
```

---

## 6. Power Distribution on HAT

| Rail | Source | Consumers |
|------|--------|-----------|
| **3.3V** | RPi Pin 1 | ADS1015 VDD, TXB0108 VCCA, encoder VCC (if 3.3V), LED current limit |
| **5V** | RPi Pin 2 | TXB0108 VCCB, button pull-ups, pot VCC, spindle sensor VCC, Molex 5V pins |
| **GND** | RPi Pins 6/9/14/20/25/30/34/39 | Common ground plane (all signals) |

**Current budget estimates:**
- 3.3V rail: ~50 mA (ADS1015 ~3 mA, TXB0108 ~1 mA, encoders ~20 mA each, misc)
- 5V rail: ~100 mA (level shifter, pull-ups, sensors, ClearPath logic ~20 mA each)

**Total HAT current draw from RPi:** < 200 mA (well within RPi PSU capacity)

---

## 7. PCB Layout Guidelines

### 7.1 Layer Stack (4-layer recommended)
| Layer | Purpose |
|-------|---------|
| Top | Components, signal traces, silkscreen labels |
| GND | Solid ground plane (thermal relief for through-holes) |
| PWR | 3.3V and 5V power planes (split or unified with vias) |
| Bottom | Signal traces (high-speed I2C, encoder signals), test points |

### 7.2 Critical Layout Rules
1. **Ground plane:** Solid unbroken ground plane on inner layer
2. **Encoder traces:** Keep A/B pairs as matched-length differential-like traces (max 50 mm, close to ground plane)
3. **STEP pulses:** Short, wide traces from TXB0108 to Molex connector (min 0.25 mm width)
4. **I2C traces:** 4.7 kΩ pull-ups within 5 mm of ADS1015 pins
5. **Decoupling:** 100 nF capacitors within 3 mm of each IC power pin
6. **Clearance:** Min 0.2 mm (8 mil) between 3.3V and 5V nets
7. **Connector placement:** 
   - Encoders: top edge of PCB
   - Motors: side edge (away from GPIO header)
   - Buttons/limits: bottom edge
   - Potentiometer: bottom edge
   - Spindle: top edge (near encoder connectors)
   - E-Stop: corner position (accessible)

### 7.3 Silkscreen Labels
- All connector pinouts labeled
- GPIO signal names next to each connector
- "MbW LATHE HAT v1.0" branding
- HAT ID EEPROM area marked
- Warning: "70V MOTOR POWER NOT ON BOARD"

---

## 8. Connector Pinout Details

### 8.1 Encoder Connector (JST PH 2.0 mm, 6-pin)
```
┌──────────────┐
│ 1 2 3 4 5 6  │  ← pins (top view)
└──────────────┘
 1: VCC (3.3V or 5V)
 2: GND
 3: Channel A
 4: Channel B
 5: INDEX (Z-axis encoder only, NC on X)
 6: NC
```

### 8.2 ClearPath Servo Signal Connector (Molex Mini-fit Jr., 8-pin)
```
 Pin 1: STEP (from TXB0108, 5V TTL)
 Pin 2: DIR (from TXB0108, 5V TTL)
 Pin 3: ENABLE (from TXB0108, 5V TTL)
 Pin 4: HLFB (Hardware Fault Feedback, to spare GPIO or NC)
 Pin 5: GND (signal ground)
 Pin 6: +5V (logic supply to ClearPath)
 Pin 7: HV+ (NOT CONNECTED on HAT — wire directly to 70V supply)
 Pin 8: HV− (NOT CONNECTED on HAT — wire directly to 70V supply)
```

**Note:** Pins 7 and 8 are for the 70V motor power. These should either be pass-through terminals on the PCB (screw terminals rated for 70V/10A) or simply not included on the signal connector. **Recommendation:** Use separate heavy-duty screw terminals for 70V power, clearly isolated from signal areas.

### 8.3 Spindle Index Connector (JST PH 2.0 mm, 3-pin)
```
 1: VCC (5V)
 2: GND
 3: SIGNAL (5V TTL → voltage divider on PCB → 3.3V to GPIO)
```

### 8.4 Potentiometer Connector (JST PH 2.0 mm, 3-pin)
```
 1: VCC (5V)
 2: Wiper (to ADS1015 A0)
 3: GND
```

### 8.5 Limit Switch Terminals (2-pin screw, 3.5 mm pitch)
```
 Pin 1: Signal (to GPIO with pull-up)
 Pin 2: GND
```
Label: LIM Z+, LIM Z−, LIM X+, LIM X−

### 8.6 Button Terminals (2-pin screw, 3.5 mm pitch)
```
 Pin 1: Signal (to GPIO with pull-up)
 Pin 2: GND
```
Label: BTN1, BTN2, BTN3, HALF-NUT

### 8.7 E-Stop Terminal (4-pin screw, 3.5 mm pitch)
```
 Pin 1: NC contact (Normally Closed — breaks on E-Stop)
 Pin 2: NO contact (Normally Open — closes on E-Stop)
 Pin 3: COM (Common)
 Pin 4: GND
```

### 8.8 70V Motor Power Terminals (Heavy-duty, 4-pin screw, 5.0 mm pitch)
```
 Pin 1: HV+ Z Motor (70V to Z ClearPath)
 Pin 2: HV− Z Motor (70V return)
 Pin 3: HV+ X Motor (70V to X ClearPath)
 Pin 4: HV− X Motor (70V return)
```
**CRITICAL:** Maintain 3 mm minimum creepage distance from all signal traces. Add isolation barrier (silkscreen warning). These are pass-through only — the 70V supply connects here, and heavy-gauge wire runs to the motors.

---

## 9. Manufacturing Notes

### 9.1 PCB Fabrication Specs
- **Board thickness:** 1.6 mm standard
- **Copper weight:** 1 oz (35 µm)
- **Min trace width:** 0.15 mm (6 mil)
- **Min via diameter:** 0.3 mm drill / 0.6 mm pad
- **Surface finish:** HASL (lead-free) or ENIG (for fine-pitch BGA if used)
- **Solder mask:** Green (standard)
- **Silkscreen:** White

### 9.2 Assembly Considerations
- TXB0108 in TSSOP-20 package (requires SMT assembly)
- ADS1015 in SOIC-16 package (requires SMT assembly)
- All resistors/capacitors in 0805 package (SMT)
- Connectors and terminals: through-hole (hand-solderable)
- LEDs: through-hole 3 mm or 5 mm

### 9.3 Estimated Cost (Prototype, 5 units)
| Item | Estimated Cost |
|------|---------------|
| PCB fabrication (4-layer, 5 pcs) | $50–100 |
| SMT components (TXB0108, ADS1015, passives) | $15–25 |
| Connectors and terminals | $20–30 |
| Assembly (manual SMT + through-hole) | Labor intensive |
| **Total per unit (prototype)** | **$25–40** |

---

## 10. Testing & Validation

### 10.1 Pre-power Checks
- [ ] Continuity: GPIO header pins to correct traces
- [ ] No shorts between 3.3V and 5V rails
- [ ] No shorts between any power rail and GND
- [ ] Level shifter VCCA/VCCB isolation

### 10.2 Power-on Tests (no load)
- [ ] 3.3V rail measures 3.3V ±5%
- [ ] 5V rail measures 5.0V ±5%
- [ ] TXB0108 outputs at 5V when inputs HIGH
- [ ] ADS1015 responds on I2C (address 0x48)

### 10.3 Functional Tests (with hardware)
- [ ] Encoder A/B signals detected by RPi
- [ ] STEP/DIR/ENABLE signals reach 5V at motor connector
- [ ] Potentiometer reads 0–4095 on ADS1015 A0
- [ ] Spindle index pulse appears on GPIO 12 at ~3.3V
- [ ] Button presses detected correctly
- [ ] Limit switch triggers detected correctly
- [ ] Half-nut switch state read correctly

---

## 11. KiCad / EAGLE Design Files

To proceed with actual PCB fabrication, the following files need to be generated:
1. **Schematic** (.kicad_sch or .sch)
2. **PCB layout** (.kicad_pcb or .brd)
3. **BOM** (.csv)
4. **Pick-and-place file** (.csv)
5. **Gerber files** (for fabrication)
6. **Drill files** (NC Drill format)

Would you like me to help generate a KiCad project structure with the schematic netlist and component footprints?

---

## 12. Safety Considerations

1. **70V isolation:** Maintain 3 mm creepage and 2.5 mm clearance from signal areas
2. **E-Stop:** Hard-wired NC contact should break the 70V enable line to motors (consider adding a relay driver on the HAT for this)
3. **Current limiting:** PTC fuse on 5V rail protects RPi from HAT shorts
4. **ESD protection:** TVS diodes on all external connector signal lines
5. **Labeling:** Clear silkscreen warnings for 70V areas

---

## 13. Future Expansion

- **Spare TXB0108 channels:** 2 channels available for future signals
- **Spare GPIO pins:** Several GPIO pins unused (SPI, UART) available for future features
- **I2C expansion:** ADS1015 has 4 channels; A1–A3 available for additional analog inputs
- **Stack-through header:** Allows chaining additional HATs on top

---

*Document version: 1.0*
*Date: 2026-07-28*
*Based on: HARDWARE.md, config.py, ARDUINO_SYSTEM_DESCRIPTION.md*
