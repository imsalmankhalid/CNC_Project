# MbW Lathe System – Hardware Compatibility List & Connection Guide

## 1. Compatible Hardware Components

### 1.1 Processing & Display

| Component | Recommended Model | Notes |
|-----------|------------------|-------|
| **Single-Board Computer** | Raspberry Pi 4 Model B (4 GB RAM) | Quad-core Cortex-A72 @ 1.8 GHz. Minimum: RPi 3B+. |
| **Touchscreen Display** | Elecrow 7" IPS HDMI 800×480 Capacitive Touch | Connects via HDMI + USB (touch). External display preferred over DSI ribbon for workshop use. |
| **microSD Card** | 32 GB Class 10 / A1 | OS + application storage. Samsung Endurance Pro recommended for industrial environments. |
| **Power Supply – RPi** | Official RPi 4 USB-C 5.1V 3A PSU | Must be stable; do **not** use phone chargers. |

### 1.2 Encoders

| Component | Model | Specification |
|-----------|-------|---------------|
| **Z-Axis Encoder** | CUI AMT103-V | 2000 CPR, quadrature, 3.3 V compatible ✓ |
| **X-Axis Encoder** | CUI AMT103-V | Same as above |
| **Encoder Cables** | CUI 435-1FT (5-pin TYCO MTA-100) | One per encoder. Custom 2 m extensions acceptable. |

### 1.3 Servo Motors & Drivers

| Component | Model | Notes |
|-----------|-------|-------|
| **Z-Axis Servo** | Teknic ClearPath SDSK (CPM-SDSK-2321S-RQN) | Any SDSK model works. Set to 800 counts/rev in MSP software. |
| **X-Axis Servo** | Teknic ClearPath SDSK | Same. |
| **Motor Signal Cable** | Teknic CPM-CABLE-CTRL-MU120 | 8-pin Molex Mini-fit, one per motor. |
| **Motor Power Cable** | Teknic CPM-CABLE-PWR-MS120 | 4-pin Molex Mini-fit, one per motor. |
| **Servo Power Supply** | 70 V DC, 7 A minimum | Generic from Amazon. Shared between both servos. |

### 1.4 Signal Level Shifting

> ⚠️ **Critical:** The RPi GPIO operates at **3.3 V**. ClearPath SDSK STEP/DIR inputs expect **5 V TTL**. Level shifters are **mandatory** for servo signals.

| Component | Model | Quantity | Notes |
|-----------|-------|----------|-------|
| **Bidirectional Level Shifter** | SparkFun BOB-12009 or TXS0108E module | 2× (one per servo) | For STEP/DIR/ENABLE (3.3 V → 5 V) |

> **Encoders (CUI AMT103-V):** Operate at 3.3 V and are **directly compatible** with RPi GPIO. No level shifter required.

### 1.5 ADC (Potentiometer)

| Component | Model | Interface | Notes |
|-----------|-------|-----------|-------|
| **ADC Module** | Adafruit ADS1115 | I2C (3.3 V) | 16-bit, 4-channel. RPi has no onboard ADC. |
| **Potentiometer** | Bourns 3547S-1AA-103A (10 kΩ) | Analog | Feed-rate control. Wire wiper to ADS1115 A0. |
| **Pot Dial** | Apem MPKES90B14 | — | Calibrated for workshop use. |

### 1.6 Safety & Inputs

| Component | Qty | Notes |
|-----------|-----|-------|
| **Limit Switches** | 4 | Normally Open (NO) contact. 3.3 V pull-up on RPi GPIO pin. One each: Z+, Z−, X+, X−. |
| **Half-Nut Lever Switch** | 1 | Same type (Omron D2HW-C213MR or equivalent). Active HIGH when engaged. |
| **E-Stop Button** | 1 | Latching NC/NO, hard-wired into servo ENABLE circuit AND RPi GPIO. |
| **Push Buttons** | 3 | 2-pin momentary, active LOW. Used for memory/zero/units (legacy support). |

### 1.7 Spindle Sensor

| Component | Model | Notes |
|-----------|-------|-------|
| **Index Pulse Card** | AutoTech C3 | Single-hole optical index. +5 V required; use separate 5 V supply or step-down from 70 V rail. |
| **Optical Sensor** | Included with C3 | Signal output is 5 V TTL → use voltage divider (10 kΩ / 20 kΩ) to get 3.3 V for RPi GPIO. |

### 1.8 Miscellaneous

| Component | Qty | Notes |
|-----------|-----|-------|
| Terminal blocks (3-pos) | 9 | Phoenix Contact 3044513 |
| DIN Rail | 1 | For terminal block mounting |
| Ethernet breakout boards | 3 | For modular RJ45 wiring (retain existing wiring harness) |
| Panel-mount RJ45 | 4 | 30 cm extension |
| 2-channel 5 V relay module | 1 | For future E-Stop hard-kill logic |
| Cable glands PG9 | 2 | Enclosure entry |

---

## 2. GPIO Pin Assignment Table (BCM Numbering)

| Signal | RPi GPIO (BCM) | Physical Pin | Direction | Notes |
|--------|---------------|-------------|-----------|-------|
| Z Encoder A | GPIO 5 | Pin 29 | Input | Pull-up via config |
| Z Encoder B | GPIO 6 | Pin 31 | Input | Pull-up via config |
| X Encoder A | GPIO 13 | Pin 33 | Input | Pull-up via config |
| X Encoder B | GPIO 19 | Pin 35 | Input | Pull-up via config |
| Spindle Index | GPIO 12 | Pin 32 | Input | 3.3 V signal (voltage-divided from 5 V) |
| Z STEP | GPIO 17 | Pin 11 | Output | Via level shifter → ClearPath |
| Z DIR | GPIO 27 | Pin 13 | Output | Via level shifter → ClearPath |
| Z ENABLE | GPIO 22 | Pin 15 | Output | Via level shifter → ClearPath |
| X STEP | GPIO 23 | Pin 16 | Output | Via level shifter → ClearPath |
| X DIR | GPIO 24 | Pin 18 | Output | Via level shifter → ClearPath |
| X ENABLE | GPIO 25 | Pin 22 | Output | Via level shifter → ClearPath |
| Button 1 | GPIO 26 | Pin 37 | Input | Active LOW, internal pull-up |
| Button 2 | GPIO 20 | Pin 38 | Input | Active LOW, internal pull-up |
| Button 3 | GPIO 21 | Pin 40 | Input | Active LOW, internal pull-up |
| Half-Nut Switch | GPIO 4 | Pin 7 | Input | Active HIGH, pull-down |
| Limit Z+ | GPIO 16 | Pin 36 | Input | Active LOW (NO switch + pull-up) |
| Limit Z− | GPIO 7 | Pin 26 | Input | Active LOW |
| Limit X+ | GPIO 8 | Pin 24 | Input | Active LOW |
| Limit X− | GPIO 11 | Pin 23 | Input | Active LOW |
| I2C SDA (ADS1115) | GPIO 2 | Pin 3 | I2C | 3.3 V I2C bus |
| I2C SCL (ADS1115) | GPIO 3 | Pin 5 | I2C | 3.3 V I2C bus |
| 3.3 V Power | — | Pin 1/17 | Power | For encoders, ADS1115 |
| 5 V Power | — | Pin 2/4 | Power | For level shifter HV side |
| GND | — | Pin 6/9/14/20/25/30/34/39 | Ground | Common ground |

---

## 3. Wiring Diagram (ASCII Schematic)

```
                        ┌─────────────────────────────┐
                        │      Raspberry Pi 4B        │
  ┌─────────────┐       │  GPIO 5/6   ← Z Encoder A/B │
  │ Z Encoder   │───────│  GPIO 13/19 ← X Encoder A/B │
  │ (AMT103-V)  │       │                             │
  └─────────────┘       │  GPIO 12 ← Spindle Index    │
  ┌─────────────┐       │            (via V-divider)  │
  │ X Encoder   │───────│                             │
  │ (AMT103-V)  │       │  GPIO 17 → Z STEP ─────────┼──→ Level ──→ ClearPath Z
  └─────────────┘       │  GPIO 27 → Z DIR  ─────────┼──→ Shifter → ClearPath Z
                        │  GPIO 22 → Z ENABLE ───────┼──→  5V    → ClearPath Z
  ┌─────────────┐       │                             │
  │ AutoTech C3 │──────→│  GPIO 12                   │  GPIO 23 → X STEP ─────┼──→ Level ──→ ClearPath X
  └─────────────┘       │  GPIO 24 → X DIR  ─────────┼──→ Shifter → ClearPath X
                        │  GPIO 25 → X ENABLE ───────┼──→  5V    → ClearPath X
  ┌─────────────┐       │                             │
  │ ADS1115 ADC │──I2C──│  GPIO 2/3 (SDA/SCL)        │
  │   + 10K Pot │       │                             │
  └─────────────┘       │  GPIO 26/20/21 ← Buttons   │
                        │  GPIO 4       ← Half-Nut   │
                        │  GPIO 16/7/8/11 ← Limits   │
                        │                             │
  ┌─────────────┐       │  HDMI ──────────────────────┼──→ 7" Touchscreen
  │  7" Touch   │──HDMI─│  USB  ──────────────────────┼──→ Touch USB
  │  Display    │──USB──│                             │
  └─────────────┘       └─────────────────────────────┘
```

---

## 4. Spindle Index Signal Conditioning

The AutoTech C3 outputs a **5 V TTL** pulse. The RPi GPIO maximum is **3.3 V**.

**Voltage divider** (10 kΩ / 20 kΩ):

```
 +5V (from C3)
      │
     10kΩ
      ├──── To GPIO 12 (RPi)   ≈ 3.33 V at output ✓
     20kΩ
      │
     GND
```

---

## 5. Level Shifter Wiring (STEP / DIR / ENABLE per axis)

Using TXS0108E or similar bidirectional level shifter:

```
  RPi (3.3 V side)   Level Shifter   ClearPath (5 V side)
  ─────────────────   ─────────────   ────────────────────
  GPIO 17 (Z STEP) → A1          B1 → STEP input
  GPIO 27 (Z DIR)  → A2          B2 → DIR input
  GPIO 22 (Z EN)   → A3          B3 → ENABLE input
  3.3 V            → VCCA       VCCB ← 5 V
  GND              → GND         GND
```

Repeat for X axis (GPIO 23/24/25 → separate shifter module).

---

## 6. E-Stop Wiring

```
                    ┌──────────────────────┐
  E-Stop Button     │  NC contact breaks    │
  (Latching NC) ────┤  the servo ENABLE     │
                    │  line hard-wired      │
                    └──────────────────────┘
                              │
                   Also wire NO contact to GPIO (any free pin)
                   for software ESTOP detection.
```

> **Safety:** Hard-wired ENABLE cut is mandatory. Software detection alone is insufficient for a machine tool.

---

## 7. Power Distribution

```
  Mains AC ─────┬─── 70 V DC Supply ──── ClearPath Z servo
                │                   └─── ClearPath X servo
                │
                └─── 5 V DC Supply ──┬── AutoTech C3 sensor
                                     └── Level Shifter (VCCB)
                                     └── (Optional) RPi backup

  RPi powered from: Official USB-C 5.1V 3A PSU (independent mains circuit)
```

---

## 8. Raspberry Pi OS Configuration

```bash
# 1. Install Raspberry Pi OS Lite (64-bit) or Desktop (64-bit)
#    Download from: https://www.raspberrypi.com/software/

# 2. Enable I2C and SPI interfaces
sudo raspi-config
# → Interface Options → I2C → Enable
# → Interface Options → SPI → Enable

# 3. Install pigpiod
sudo apt-get install pigpio python3-pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 4. Install project dependencies
cd /home/pi/lathe_rpi
pip3 install -r requirements.txt

# 5. (Optional) Install PREEMPT_RT kernel for better real-time performance
#    See: https://lemariva.com/blog/2019/09/raspberry-pi-4-preempt-rt-kernel

# 6. Start application on boot
sudo cp lathe.service /etc/systemd/system/
sudo systemctl enable lathe
sudo systemctl start lathe
```

### `lathe.service` (systemd unit)
```ini
[Unit]
Description=MbW Lathe Control System
After=pigpiod.service network.target

[Service]
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/usr/bin/python3 /home/pi/lathe_rpi/main.py
WorkingDirectory=/home/pi/lathe_rpi
User=pi
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
