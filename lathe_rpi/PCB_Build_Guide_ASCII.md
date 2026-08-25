# MbW Lathe HAT – Corrected PCB Build Guide (12V + RPi Native USB-C)

The Raspberry Pi powers itself through its **own USB-C port** (already on the board).
The HAT only adds a **12V DC jack**. Power flows through the GPIO header pins.

---

## Power Concept (Corrected)

```
  Scenario A — 12V Connected (Normal Operation):
  ═══════════════════════════════════════════════

  ┌──────────┐    ┌──────┐    ┌──────────┐    ┌──────────┐
  │ 12V DC   │───→│ Fuse │───→│ MP2307   │───→│ 5V0 Rail │
  │ Jack     │    │  1A  │    │ Buck     │    │          │
  │ (J17)    │    └──────┘    │ 12V→5V   │    │    ┌─────┴─────┐
  └──────────┘                └──────────┘    │    │           │
                                              │    │  ┌────────┴──────┐
  ┌──────────┐                ┌──────────┐    │    │  │ ┌────────────┴──┐
  │ (also)   │                │ AP2112   │    │    │  │ │ RPi GPIO Header
  │ VIN_12V  │───────────────→│ LDO      │───→┼────┤  │ │ Pin 2 → 5V   │
  └──────────┘                │ 12V→3.3V │    │    │  │ │ Pin 1 → 3.3V │
                              └──────────┘    │    │  │ │ (powers RPi) │
                                              │    │  │ └──────────────┘
                                              │    │  └────────────────
                                              │    │
                                         HAT 5V0│  HAT 3V3
                                         logic  │  logic
                                              └────┘


  Scenario B — USB-C Only (Bench / Debug, No 12V):
  ═══════════════════════════════════════════════

  ┌──────────────┐
  │ RPi USB-C    │  ← User plugs USB-C cable into RPi's OWN port
  │ (native)     │
  └──────┬───────┘
         │ RPi generates 5V and 3.3V internally
         │
         │ Back-fed through GPIO header:
         │  Pin 2 (5V)  ──→ HAT 5V0 rail
         │  Pin 1 (3.3V) ──→ HAT 3V3 rail
         │
         │ HAT regulators are OFF (no 12V input)
         │ HAT logic runs from RPi back-fed power ✓
```

---

## Step 0 — Base: Raspberry Pi + GPIO Header

```
                    ┌──────────────────────────────────────────────┐
                    │           RPi 4 / 40-Pin GPIO                │
                    │                                              │
  USB-C Port ──────→│  (RPi's native USB-C, NOT on HAT)           │
  (on RPi board)    │                                              │
                    │  ┌────────────────────────────────────┐      │
                    │  │  2×20 Male Header (J1) on HAT      │      │
                    │  │                                    │      │
  Row A (odd)  ────→│  │  1   3   5   7   9  11  13  15 17 19  │      │
                    │  │ ┌───┬───┬───┬───┬──┬──┬──┬──┬──┬──┐  │      │
  Row B (even) ───→│  │ │ 2 │ 4 │ 6 │ 8 │10│12│14│16│18│20│  │      │
                    │  │ └───┴───┴───┴───┴──┴──┴──┴──┴──┴──┘  │      │
                    │  │  21  23  25  27  29 31 33 35 37 39  │      │
                    │  │ ┌───┬───┬───┬───┬──┬──┬──┬──┬──┬──┐  │      │
                    │  │ │21 │23 │25 │27 │29│31│33│35│37│39│  │      │
                    │  │ └───┴───┴───┴───┴──┴──┴──┴──┴──┴──┘  │      │
                    │  │  40  (Pin 40 = GPIO 21 = BTN3)       │      │
                    │  └────────────────────────────────────┘      │
                    └──────────────────────────────────────────────┘

  Pins we use:
  ┌────────┬──────────┬────────────────────────────────┐
  │ Pin    │ Signal   │ Purpose                        │
  ├────────┼──────────┼────────────────────────────────┤
  │ 1, 17  │ 3.3V     │ Power (source or sink)         │
  │ 2, 4   │ 5V       │ Power (source or sink)         │
  │ 3      │ GPIO 2   │ I2C SDA → ADS1015              │
  │ 5      │ GPIO 3   │ I2C SCL → ADS1015              │
  │ 7      │ GPIO 4   │ Half-nut switch                │
  │ 11     │ GPIO 17  │ Z STEP → 74HC245               │
  │ 13     │ GPIO 27  │ Z DIR  → 74HC245               │
  │ 15     │ GPIO 22  │ Z EN   → 74HC245               │
  │ 16     │ GPIO 23  │ X DIR  → 74HC245               │
  │ 18     │ GPIO 24  │ X STEP → 74HC245               │
  │ 22     │ GPIO 25  │ X EN   → 74HC245               │
  │ 23     │ GPIO 11  │ Limit X−                       │
  │ 24     │ GPIO 8   │ Limit X+                       │
  │ 26     │ GPIO 7   │ Limit Z−                       │
  │ 29     │ GPIO 5   │ Z Encoder A                    │
  │ 31     │ GPIO 6   │ Z Encoder B                    │
  │ 32     │ GPIO 12  │ Spindle index                  │
  │ 33     │ GPIO 13  │ X Encoder A                    │
  │ 35     │ GPIO 19  │ X Encoder B                    │
  │ 36     │ GPIO 16  │ Limit Z+                       │
  │ 37     │ GPIO 26  │ Button 1                       │
  │ 38     │ GPIO 20  │ Button 2                       │
  │ 40     │ GPIO 21  │ Button 3                       │
  │ 6,9,14 │ GND      │ Ground (multiple)              │
  │ 20,25,30,34,39 │ GND │ Ground (more)            │
  └────────┴──────────┴────────────────────────────────┘
```

---

## Step 1 — 12V Power Input (Only New Power Connector)

```
  Top Edge of Board:

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │   ┌──────────┐                                                 │
  │   │ DC Jack  │  5.5mm × 2.1mm barrel jack                      │
  │   │  (J17)   │  Center = +12V, Sleeve = GND                    │
  │   └────┬─────┘                                                 │
  │        │                                                       │
  │        │  ┌── Center (tip) = VIN_12V_RAW                       │
  │        │  │                                                     │
  │        │  │  ┌── Sleeve = GND ──────────────────────────────┐  │
  │        ▼  │                                                 ▼  │
  │   ┌──────────┐                                            GND  │
  │   │ F1: 1A   │  Slow-blow fuse, 1206 SMD                    │
  │   │ slow-blow│                                                 │
  │   └────┬─────┘                                                 │
  │        │ VIN_12V (after fuse)                                  │
  │        │                                                       │
  │        ├────────────────────────────────┐                      │
  │        │                                │                      │
  │        ▼                                ▼                      │
  │   ┌──────────┐                    ┌──────────┐                 │
  │   │ D8       │                    │ C7       │                 │
  │   │SMAJ13CA  │                    │10µF 25V  │                 │
  │   │ (TVS)    │                    │ (1206)   │                 │
  │   │ to GND   │                    │ to GND   │                 │
  │   └──────────┘                    └──────────┘                 │
  │        │                                │                      │
  │        │  ┌──────────┐                  │                      │
  │        │  │ C8       │                  │                      │
  │        │  │100nF     │                  │                      │
  │        │  │ to GND   │                  │                      │
  │        │  └──────────┘                  │                      │
  │        │                                │                      │
  │        ▼                                ▼                      │
  │   ═══════════════════════════════════════════                  │
  │   VIN_12V rail (protected, clean 12V)                          │
  │   ═══════════════════════════════════════════                  │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

**Wired connections from DC jack:**
```
  DC Jack center pin  ──── copper trace ────→  F1 pad 1 (fuse input)
  F1 pad 2 (fuse output) ──── copper trace ────→ VIN_12V net
  VIN_12V net ──── copper trace ────→  D8 anode (TVS cathode to GND)
  VIN_12V net ──── copper trace ────→  C7 positive (C7 negative to GND)
  VIN_12V net ──── copper trace ────→  C8 positive (C8 negative to GND)
  DC Jack sleeve  ──── copper trace ────→  GND plane
```

---

## Step 2 — 5V Buck Regulator (MP2307: 12V → 5V)

```
  Position: Near DC jack, top area of board

  Wired connections (trace-by-trace):

  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  VIN_12V rail ──────────────────────────────────────────────┼─→ MP2307 Pin 1 (VIN)
  │                                                             │
  │  GND plane  ────────────────────────────────────────────────┼─→ MP2307 Pin 4 (GND)
  │  GND plane  ────────────────────────────────────────────────┼─→ MP2307 Pin 8 (GND)
  │                                                             │
  │  3V3 rail   ────────────────────────────────────────────────┼─→ MP2307 Pin 2 (EN)
  │           (enable buck when 3.3V is present —               │
  │            either from LDO or RPi back-feed)                │
  │                                                             │
  │  GND plane  ────────────────────────────────────────────────┼─→ MP2307 Pin 7 (FB)
  │           (fixed 5V variant: FB tied to GND)                │
  │                                                             │
  │  MP2307 Pin 6 (RT) ─── R24 (22kΩ) ─── GND plane            │
  │                                                             │
  │  MP2307 Pin 3 (SW) ────┬───────────────────────────────────┼─→ L1 (10µH) one end
  │                        │ SW node (NOISY — keep trace short) │
  │                        │                                    │
  │  MP2307 Pin 5 (BOOT) ──┴── C11 (100nF) other end           │
  │           (bootstrap cap between BOOT and SW)               │
  │                                                             │
  │  L1 (10µH) other end ────┬──→ D9 (SS34) anode              │
  │                          │                                  │
  │                          │                                  │
  │                     D9 cathode ────→ 5V0_BUCK net          │
  │                                                             │
  │  5V0_BUCK ──── C9 (22µF 16V) ──── GND                     │
  │  5V0_BUCK ──── C10 (100nF)   ──── GND                     │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

  ASCII schematic of buck:

       VIN_12V                    MP2307 (U3)                   5V0_BUCK
       ────────┐                  ┌────────────┐                ────────
               │                  │            │                       │
               ├─────────────────→│ 1     8 ├─→┘ (GND)                │
               │                  │            │                       │
      3V3 ─────┼─────────────────→│ 2     7 ├─→┘ (GND = FB)           │
               │                  │            │                       │
               │                  │ 3     6 ├─→┬── 22kΩ ─── GND       │
               │                  │            │    │                  │
               │                  │ SW    RT │    │                  │
               │                  │            │    │                  │
               │                  │ 4     5 ├─→┬── 100nF ───┐         │
               │                  │            │      │      │         │
      GND ─────┼─────────────────→│ GND BOOT │      │      │         │
               │                  └────┬─────┘      │      │         │
               │                       │ SW         │      │         │
               │                       │            │      │         │
               │                       ├────────────┘      │         │
               │                       │ (SW node)         │         │
               │                       │                   │         │
               │                  ┌────┴────┐              │         │
               │                  │   L1    │              │         │
               │                  │  10µH   │              │         │
               │                  └────┬────┘              │         │
               │                       │                   │         │
               │                  ┌────┴────┐              │         │
               │                  │    D9   │              │         │
               │                  │  SS34   │              │         │
               │                  │ ─|<|──  │              │         │
               │                  └────┬────┘              │         │
               │                       │ 5V0_BUCK          │         │
               │                  ┌────┴──────────┐        │         │
               │                  │ C9: 22µF 16V  │        │         │
               │                  │ C10: 100nF    │        │         │
               │                  └────┬──────────┘        │         │
      GND ─────┼───────────────────────┘                    │         │
               │                                            │         │
               └────────────────────────────────────────────┘         │
```

---

## Step 3 — 3.3V LDO Regulator (AP2112: 12V → 3.3V)

```
  Position: Near buck regulator, top area

  Wired connections:

  VIN_12V rail ────────────────────────────────────────→ AP2112 Pin 1 (VIN)
  GND plane  ──────────────────────────────────────────→ AP2112 Pin 2 (GND)
  GND plane  ──────────────────────────────────────────→ AP2112 Pin 3 (GND)
  GND plane  ──────────────────────────────────────────→ AP2112 thermal pad

  AP2112 Pin 4 (VOUT) ────→ 3V3_REG net

  3V3_REG ──── C13 (10µF 6.3V) ──── GND        (required for LDO stability)
  3V3_REG ──── C14 (100nF)     ──── GND

  VIN_12V ──── C12 (10µF 16V) ──── GND         (LDO input cap)

  ASCII schematic:

       VIN_12V                                     3V3_REG
       ────────┐                                   ────────
               │                                           │
               │      ┌──────────┐                        │
               │      │          │                        │
               ├──────┤ 1      4 ├────────────────────────┤
               │      │ AP2112   │                        │
               │      │ 3.3V LDO │                        │
               │      │          │                        │
               ├──────┤ 2      3 ├────────────────────────┤
               │      │          │                        │
      GND ─────┼──────┘          └────────────────────────┘
               │            ▭ (thermal pad)
               │            └──→ GND (3+ thermal vias)
               │
          ┌────┴────┐
          │  C12    │
          │ 10µF 16V│
          └────┬────┘
               │
              GND

                          3V3_REG
                            │
                       ┌────┴────┐
                       │  C13    │
                       │ 10µF 6.3V│
                       └────┬────┘
                            │
                           GND

                          3V3_REG
                            │
                       ┌────┴────┐
                       │  C14    │
                       │ 100nF   │
                       └────┬────┘
                            │
                           GND
```

---

## Step 4 — Power Diode OR-ing (Simplified: No USB-C on HAT)

```
  This is the KEY circuit. It lets the HAT work with 12V OR with RPi USB-C only.

  ═══════════════════════════════════════════════════════════════════
  5V Rail OR-ing
  ═══════════════════════════════════════════════════════════════════

  When 12V present:  Buck outputs 5V → D11 conducts → 5V0 rail active
  When no 12V:       RPi (powered by USB-C) outputs 5V on Pin 2 → D12 conducts → 5V0 rail active

         Buck Output                    RPi GPIO Pin 2
         (5V0_BUCK)                     (5V from RPi USB-C)
              │                              │
              │                          ┌───┴───┐
              │                          │  J1   │
              │                          │Pin 2  │
              │                          │(GPIO) │
              │                          └───┬───┘
              │                              │
           ┌──┴──┐                      ┌───┴───┐
           │ D11 │                      │  D12  │
           │SS34 │                      │ SS34  │
           │ ─|< │                      │  ─|< │
           └──┬──┘                      └───┬───┘
              │  cathode                    │  cathode
              │                             │
              └──────────┬──────────────────┘
                         │
                         ▼
                       5V0 ────────────────────────────────────────
                         │                                         │
                    ┌────┴────┐                                    │
                    │  C5     │                                    │
                    │ 10µF    │                                    │
                    └────┬────┘                                    │
                         │                                         │
                        GND                                       │
                                                                   │
                    This 5V0 rail feeds:                           │
                    - 74HC245 VCC (Pin 20)                        │
                    - Servo connectors J4/J5 Pin 6                │
                    - Potentiometer J7 Pin 1                      │
                    - Spindle J6 Pin 1                            │
                    - Button/limit pull-up resistors              │


  ═══════════════════════════════════════════════════════════════════
  3.3V Rail OR-ing
  ═══════════════════════════════════════════════════════════════════

  When 12V present:  LDO outputs 3.3V → D14 conducts → 3V3 rail active
  When no 12V:        RPi (powered by USB-C) outputs 3.3V on Pin 1 → D15 conducts → 3V3 rail active

         LDO Output                     RPi GPIO Pin 1 (and Pin 17)
         (3V3_REG)                      (3.3V from RPi)
              │                              │
              │                          ┌───┴───┐
              │                          │  J1   │
              │                          │Pin 1,17│
              │                          │ (GPIO) │
              │                          └───┬───┘
              │                              │
           ┌──┴──┐                      ┌───┴───┐
           │ D14 │                      │  D15  │
           │SS34 │                      │ SS34  │
           │ ─|< │                      │  ─|< │
           └──┬──┘                      └───┬───┘
              │  cathode                    │  cathode
              │                             │
              └──────────┬──────────────────┘
                         │
                         ▼
                       3V3 ────────────────────────────────────────
                         │                                         │
                    ┌────┴────┐                                    │
                    │  C6     │                                    │
                    │ 10µF    │                                    │
                    └────┬────┘                                    │
                         │                                         │
                        GND                                       │
                                                                   │
                    This 3V3 rail feeds:                           │
                    - ADS1015 VDD (Pin 5, 9)                      │
                    - Encoder connectors J2/J3 Pin 1              │
                    - All pull-up resistors (buttons, limits)     │
                    - I2C pull-up resistors                       │
```

---

## Step 5 — 74HC245 Level Shifter (3.3V → 5V)

```
  Position: Center of board, just above GPIO header

  ┌────────────────────────────────────────────────────────────────┐
  │                                                                │
  │  Power connections:                                            │
  │  ─────────────────                                             │
  │                                                                │
  │  5V0 rail ────────────────────────────────────────────────────┼─→ Pin 20 (VCC)
  │  GND plane ───────────────────────────────────────────────────┼─→ Pin 9  (GND)
  │  5V0 rail ────────────────────────────────────────────────────┼─→ Pin 11 (DIR = HIGH, A→B direction)
  │  GND plane ───────────────────────────────────────────────────┼─→ Pin 10 (/CE = LOW, chip enabled)
  │                                                                │
  │  C1 (100nF) from Pin 20 to GND (within 2mm!)                  │
  │                                                                │
  │  Signal connections (wired trace-by-trace):                    │
  │  ───────────────────────────────────────────────────────────── │
  │                                                                │
  │  ┌────────────┐   ┌──────────────────┐   ┌──────────────┐    │
  │  │ RPi GPIO   │   │   74HC245 (U1)   │   │  To Connector│    │
  │  │  (3.3V)    │   │   TSSOP-20       │   │   (5V)       │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │ J1 Pin 11  │──→│ Pin 1  (A1)      │──→│ Pin 12 (B1)  │    │
  │  │ GPIO 17    │   │                  │   │              │    │
  │  │ Z STEP     │   │  3.3V in → 5V out│   │ Z_STEP_5V    │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │            │   │                  │   │              │    │
  │  │ J1 Pin 13  │──→│ Pin 2  (A2)      │──→│ Pin 13 (B2)  │    │
  │  │ GPIO 27    │   │                  │   │              │    │
  │  │ Z DIR      │   │                  │   │ Z_DIR_5V     │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │            │   │                  │   │              │    │
  │  │ J1 Pin 15  │──→│ Pin 3  (A3)      │──→│ Pin 14 (B3)  │    │
  │  │ GPIO 22    │   │                  │   │              │    │
  │  │ Z ENABLE   │   │                  │   │ Z_EN_5V      │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │            │   │                  │   │              │    │
  │  │ J1 Pin 18  │──→│ Pin 4  (A4)      │──→│ Pin 15 (B4)  │    │
  │  │ GPIO 24    │   │                  │   │              │    │
  │  │ X STEP     │   │                  │   │ X_STEP_5V    │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │            │   │                  │   │              │    │
  │  │ J1 Pin 16  │──→│ Pin 5  (A5)      │──→│ Pin 16 (B5)  │    │
  │  │ GPIO 23    │   │                  │   │              │    │
  │  │ X DIR      │   │                  │   │ X_DIR_5V     │    │
  │  ├────────────┤   ├──────────────────┤   ├──────────────┤    │
  │  │            │   │                  │   │              │    │
  │  │ J1 Pin 22  │──→│ Pin 6  (A6)      │──→│ Pin 17 (B6)  │    │
  │  │ GPIO 25    │   │                  │   │              │    │
  │  │ X ENABLE   │   │                  │   │ X_EN_5V      │    │
  │  └────────────┘   └──────────────────┘   └──────┬───────┘    │
  │                                                  │            │
  │                                         From B1/B4: 100Ω resistor → connector
  │                                         From B2/B3/B5/B6: direct → connector
  │                                                                │
  │  Pins 7,8 (A7,A8) and 18,19 (B7,B8): unconnected (spare)     │
  │                                                                │
  └────────────────────────────────────────────────────────────────┘

  Physical pin layout (TSSOP-20, top view):

         ┌─────────────┐
   A1 ───┤ 1         20├─── VCC (5V0)
   A2 ───┤ 2         19├─── B8 (spare)
   A3 ───┤ 3         18├─── B7 (spare)
   A4 ───┤ 4         17├─── B6 ───→ X_EN_5V
   A5 ───┤ 5         16├─── B5 ───→ X_DIR_5V
   A6 ───┤ 6         15├─── B4 ───→ X_STEP_5V
   A7 ───┤ 7         14├─── B3 ───→ Z_EN_5V
   A8 ───┤ 8         13├─── B2 ───→ Z_DIR_5V
  GND ───┤ 9         12├─── B1 ───→ Z_STEP_5V
  /CE ───┤10         11├─── DIR (5V0 = HIGH)
         └─────────────┘
```

---

## Step 6 — ADS1015 ADC (Potentiometer)

```
  Position: Bottom-right area, near pot connector J7

  Wired connections:

  3V3 rail ─────────────────────────────────────────────→ ADS1015 Pin 5 (DVDD)
  3V3 rail ─────────────────────────────────────────────→ ADS1015 Pin 9 (AVDD)
  GND plane ────────────────────────────────────────────→ ADS1015 Pin 4 (GND)
  GND plane ────────────────────────────────────────────→ ADS1015 Pin 6 (DVSS)
  GND plane ────────────────────────────────────────────→ ADS1015 Pin 10 (AVSS)
  GND plane ────────────────────────────────────────────→ ADS1015 Pin 3 (A0 = I2C addr 0x48)

  I2C_SDA net ──────────────────────────────────────────→ ADS1015 Pin 1 (SDA)
  I2C_SCL net ──────────────────────────────────────────→ ADS1015 Pin 2 (SCL)

  POT_WIPER ─── R9 (10kΩ) ───→ ADS1015 Pin 7 (AIN0)

  Decoupling (CRITICAL — place directly across pins):
  C2 (100nF): Pin 9 (AVDD) ↔ Pin 10 (AVSS)
  C3 (100nF): Pin 5 (DVDD) ↔ Pin 6 (DVSS)
  C4 (10µF):  3V3 rail ↔ GND (near chip)

  ADS1015 VSSOP-10 pinout:

       ┌────────────┐
  SDA ─┤ 1         10├── AVDD (3V3)
  SCL ─┤ 2          9├── DVDD (3V3)
  GND ─┤ 3          8├── AIN1 (spare)
  GND ─┤ 4          7├── AIN0 ← Pot wiper (via R9 10kΩ)
  3V3 ─┤ 5          6├── DVSS (GND)
       └────────────┘
       (3×3 mm package)

  Potentiometer connector (J7):

       ┌──────────┐
       │  J7      │  JST PH 3-pin
       │          │
       │ Pin 1 ───┼──→ 5V0 rail (pot end A, powered from 5V)
       │ Pin 2 ───┼──→ POT_WIPER net ───→ R9 (10kΩ) ───→ ADS1015 AIN0
       │ Pin 3 ───┼──→ GND (pot end B)
       └──────────┘
```

---

## Step 7 — I2C Bus (SDA + SCL with Pull-ups)

```
  Wired connections:

  RPi GPIO Header              ADS1015
  ┌─────────────┐              ┌─────────────┐
  │ J1 Pin 3    │──────────────│ Pin 1       │
  │ (GPIO 2)    │  I2C_SDA     │ (SDA)       │
  └──────┬──────┘              └─────────────┘
         │
         │ I2C_SDA trace
         │
         ├────────────────────────────────────┐
         │                                    │
      ┌──┴──┐                            (to other I2C
      │ R22 │                            devices if added)
      │4.7kΩ│
      └──┬──┘
         │
        3V3


  RPi GPIO Header              ADS1015
  ┌─────────────┐              ┌─────────────┐
  │ J1 Pin 5    │──────────────│ Pin 2       │
  │ (GPIO 3)    │  I2C_SCL     │ (SCL)       │
  └──────┬──────┘              └─────────────┘
         │
         │ I2C_SCL trace
         │
         ├────────────────────────────────────┐
         │                                    │
      ┌──┴──┐
      │ R23 │
      │4.7kΩ│
      └──┬──┘
         │
        3V3

  NO capacitors on I2C lines! Keep traces < 5cm.
```

---

## Step 8 — Encoders (Z + X Axis)

```
  Position: Left edge of board

  ┌────────────────────────────────────────────────────────┐
  │                                                        │
  │  J2 — Z-Axis Encoder (JST PH 6-pin)                   │
  │  ─────────────────────────────────────────              │
  │                                                        │
  │  ┌──────────┐                                         │
  │  │  J2      │                                         │
  │  │          │  Wired connections:                     │
  │  │ Pin 1 ───┼──────────────────────────────→ 3V3 rail │
  │  │ Pin 2 ───┼──────────────────────────────→ GND      │
  │  │ Pin 3 ───┼── Z_ENC_A ───→ J1 Pin 29 (GPIO 5)      │
  │  │ Pin 4 ───┼── Z_ENC_B ───→ J1 Pin 31 (GPIO 6)      │
  │  │ Pin 5 ───┼── (unconnected)                        │
  │  │ Pin 6 ───┼── (unconnected)                        │
  │  └──────────┘                                         │
  │                                                        │
  │  Optional pull-ups (place near connector, DNP if not): │
  │  R1 (10kΩ): Z_ENC_A ───→ 3V3                          │
  │  R2 (10kΩ): Z_ENC_B ───→ 3V3                          │
  │                                                        │
  │  ───────────────────────────────────────────────────── │
  │                                                        │
  │  J3 — X-Axis Encoder (JST PH 6-pin)                   │
  │  ─────────────────────────────────────────              │
  │                                                        │
  │  ┌──────────┐                                         │
  │  │  J3      │                                         │
  │  │          │  Wired connections:                     │
  │  │ Pin 1 ───┼──────────────────────────────→ 3V3 rail │
  │  │ Pin 2 ───┼──────────────────────────────→ GND      │
  │  │ Pin 3 ───┼── X_ENC_A ───→ J1 Pin 33 (GPIO 13)     │
  │  │ Pin 4 ───┼── X_ENC_B ───→ J1 Pin 35 (GPIO 19)     │
  │  │ Pin 5 ───┼── (unconnected)                        │
  │  │ Pin 6 ───┼── (unconnected)                        │
  │  └──────────┘                                         │
  │                                                        │
  │  R3 (10kΩ): X_ENC_A ───→ 3V3                          │
  │  R4 (10kΩ): X_ENC_B ───→ 3V3                          │
  │                                                        │
  └────────────────────────────────────────────────────────┘
```

---

## Step 9 — Servo Signal Connectors (Z + X Axis)

```
  Position: Right edge of board

  ┌────────────────────────────────────────────────────────────────┐
  │                                                                │
  │  J4 — Z-Axis Servo (Molex KK-254 8-pin)                       │
  │  ──────────────────────────────────────────                    │
  │                                                                │
  │  ┌──────────────┐                                             │
  │  │    J4        │                                             │
  │  │              │  Wired connections:                         │
  │  │ Pin 1 (STEP) │←── R5 (100Ω) ←── Z_STEP_5V ← 74HC245 B1   │
  │  │ Pin 2 (DIR)  │←── R6 (100Ω) ←── Z_DIR_5V  ← 74HC245 B2   │
  │  │ Pin 3 (EN)   │←─────────────── Z_EN_5V   ← 74HC245 B3    │
  │  │ Pin 4 (HLFB) │←── (unconnected)                                │
  │  │ Pin 5 (GND)  │←─────────────── GND plane                    │
  │  │ Pin 6 (5V)   │←─────────────── 5V0 rail                     │
  │  │ Pin 7 (HV+)  │←── (unconnected, 70V external)              │
  │  │ Pin 8 (HV-)  │←── (unconnected, 70V external)              │
  │  └──────────────┘                                             │
  │                                                                │
  │  TVS diodes (signal → GND):                                   │
  │  D1: Z_STEP_5V → GND   D2: Z_DIR_5V → GND   D3: Z_EN_5V → GND│
  │                                                                │
  │  ────────────────────────────────────────────────────────────  │
  │                                                                │
  │  J5 — X-Axis Servo (Molex KK-254 8-pin)                       │
  │  ──────────────────────────────────────────                    │
  │                                                                │
  │  ┌──────────────┐                                             │
  │  │    J5        │                                             │
  │  │              │  Wired connections:                         │
  │  │ Pin 1 (STEP) │←── R7 (100Ω) ←── X_STEP_5V ← 74HC245 B4   │
  │  │ Pin 2 (DIR)  │←── R8 (100Ω) ←── X_DIR_5V  ← 74HC245 B5   │
  │  │ Pin 3 (EN)   │←─────────────── X_EN_5V   ← 74HC245 B6    │
  │  │ Pin 4 (HLFB) │←── (unconnected)                                │
  │  │ Pin 5 (GND)  │←─────────────── GND plane                    │
  │  │ Pin 6 (5V)   │←─────────────── 5V0 rail                     │
  │  │ Pin 7 (HV+)  │←── (unconnected, 70V external)              │
  │  │ Pin 8 (HV-)  │←── (unconnected, 70V external)              │
  │  └──────────────┘                                             │
  │                                                                │
  │  D4: X_STEP_5V → GND   D5: X_DIR_5V → GND   D6: X_EN_5V → GND│
  │                                                                │
  └────────────────────────────────────────────────────────────────┘
```

---

## Step 10 — Spindle Index

```
  Position: Right edge, near servo connectors

  ┌─────────────────────────────────────────┐
  │                                         │
  │  J6 — Spindle Index (JST PH 3-pin)     │
  │  ─────────────────────────────────────  │
  │                                         │
  │  ┌──────────┐                           │
  │  │  J6      │                           │
  │  │          │  Wired connections:       │
  │  │ Pin 1 ───┼──→ 5V0 rail              │
  │  │ Pin 2 ───┼──→ GND                   │
  │  │ Pin 3 ───┼──→ SPINDLE_RAW net       │
  │  └──────────┘                           │
  │                                         │
  │  SPINDLE_RAW trace:                     │
  │  ─────────────────                      │
  │                                         │
  │  SPINDLE_RAW ──── D7 (TVS) ──── GND    │
  │       │                                  │
  │       ▼                                  │
  │  ┌──────────┐                           │
  │  │  R10     │  10kΩ (divider top)       │
  │  │  10kΩ    │                           │
  │  └────┬─────┘                           │
  │       │                                  │
  │       ├────→ SPINDLE_IN ───→ J1 Pin 32  │
  │       │         (~3.33V)     (GPIO 12)  │
  │  ┌────┴─────┐                           │
  │  │  R11     │  20kΩ (divider bottom)    │
  │  │  20kΩ    │                           │
  │  └────┬─────┘                           │
  │       │                                  │
  │      GND                                 │
  │                                         │
  │  Voltage divider schematic:             │
  │                                         │
  │     SPINDLE_RAW (5V from AutoTech C3)   │
  │          │                               │
  │        10kΩ (R10)                        │
  │          │                               │
  │          ├──── SPINDLE_IN → GPIO 12      │
  │        20kΩ (R11)                        │
  │          │                               │
  │         GND                              │
  │                                         │
  │  Output: 5V × 20/(10+20) = 3.33V ✓     │
  │                                         │
  └─────────────────────────────────────────┘
```

---

## Step 11 — Buttons, Half-Nut, Limit Switches, E-Stop

```
  Position: Bottom edge of board, left to right

  ═══════════════════════════════════════════════════════════════════
  Buttons (Active LOW — switch closes to GND, pull-up to 3V3)
  ═══════════════════════════════════════════════════════════════════

  ┌────────┐         ┌────────┐         ┌────────┐
  │  J8    │         │  J9    │         │  J10   │
  │ BTN1   │         │ BTN2   │         │ BTN3   │
  │ 2-pin  │         │ 2-pin  │         │ 2-pin  │
  └──┬──┬──┘         └──┬──┬──┘         └──┬──┬──┘
     │  │                │  │                │  │
  Pin1│  │Pin2         Pin1│  │Pin2         Pin1│  │Pin2
     │  │                │  │                │  │
     │  │GND             │  │GND             │  │GND
     ▼  │                ▼  │                ▼  │
  BTN1 │              BTN2 │              BTN3 │
  _IN  │              _IN  │              _IN  │
     │  │                │  │                │  │
   ┌─┴──┴──┐          ┌─┴──┴──┐          ┌─┴──┴──┐
   │  R12  │          │  R13  │          │  R14  │
   │ 10kΩ  │          │ 10kΩ  │          │ 10kΩ  │
   └─┬     ┘          └─┬     ┘          └─┬     ┘
     │                  │                  │
    3V3                3V3                3V3

  Wired to GPIO:
  BTN1_IN  ───→ J1 Pin 37 (GPIO 26)
  BTN2_IN  ───→ J1 Pin 38 (GPIO 20)
  BTN3_IN  ───→ J1 Pin 40 (GPIO 21)


  ═══════════════════════════════════════════════════════════════════
  Half-Nut Switch (Active HIGH — switch closes to 3V3, pull-down)
  ═══════════════════════════════════════════════════════════════════

  ┌────────┐
  │  J11   │
  │HALF-NUT│
  │ 2-pin  │
  └──┬──┬──┘
     │  │
  Pin1│  │Pin2
     │  │
     │  │GND
     ▼  │
  HALF- │
  _NUT_ │
   IN   │
     │  │
   ┌─┴──┴──┐
   │  R15  │
   │ 10kΩ  │  ← PULL-DOWN (not pull-up!)
   └─┬     ┘
     │
    GND

  Wired to GPIO:
  HALF_NUT_IN ───→ J1 Pin 7 (GPIO 4)


  ═══════════════════════════════════════════════════════════════════
  Limit Switches (NC contact, pull-up to 3V3)
  ═══════════════════════════════════════════════════════════════════

  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
  │ J12    │  │ J13    │  │ J14    │  │ J15    │
  │ LIM Z+ │  │ LIM Z- │  │ LIM X+ │  │ LIM X- │
  │ 2-pin  │  │ 2-pin  │  │ 2-pin  │  │ 2-pin  │
  └──┬──┬──┘  └──┬──┬──┘  └──┬──┬──┘  └──┬──┬──┘
     │  │         │  │         │  │         │  │
  Pin1│  │Pin2  Pin1│  │Pin2  Pin1│  │Pin2  Pin1│  │Pin2
     │  │GND      │  │GND      │  │GND      │  │GND
     ▼  │         ▼  │         ▼  │         ▼  │
  LIM_Z│       LIM_Z│       LIM_X│       LIM_X│
  _PLUS│       _MINUS│      _PLUS│       _MINUS│
  _IN  │        _IN │       _IN  │        _IN │
     │  │         │  │         │  │         │  │
   ┌─┴──┴──┐   ┌─┴──┴──┐   ┌─┴──┴──┐   ┌─┴──┴──┐
   │  R16  │   │  R17  │   │  R18  │   │  R19  │
   │ 10kΩ  │   │ 10kΩ  │   │ 10kΩ  │   │ 10kΩ  │
   └─┬     ┘   └─┬     ┘   └─┬     ┘   └─┬     ┘
     │           │           │           │
    3V3         3V3         3V3         3V3

  Wired to GPIO:
  LIM_Z_PLUS_IN  ───→ J1 Pin 36 (GPIO 16)
  LIM_Z_MINUS_IN ───→ J1 Pin 26 (GPIO 7)
  LIM_X_PLUS_IN  ───→ J1 Pin 24 (GPIO 8)
  LIM_X_MINUS_IN ───→ J1 Pin 23 (GPIO 11)


  ═══════════════════════════════════════════════════════════════════
  E-Stop (4-pin)
  ═══════════════════════════════════════════════════════════════════

  ┌──────────────┐
  │    J16       │
  │   E-STOP     │
  │   4-pin      │
  └──┬──┬──┬──┬──┘
     │  │  │  │
  Pin1│  │  │  │Pin4
     │  │  │  │
     │  │  │  │GND
     │  │  │  │
     │  │  │  │
     │  │  │  └───────────────────────────────────────→ GND
     │  │  │
     │  │  └── Pin 3 (COM) ───→ ESTOP_COM net
     │  │
     │  └── Pin 2 (NO)  ───→ ESTOP_IN ───→ J1 Pin ?? (free GPIO)
     │                              + R20 (10kΩ pull-up to 3V3)
     │
     └── Pin 1 (NC)  ───→ ESTOP_NC
              → Hard-wired in series with servo ENABLE traces
              → When E-Stop pressed, NC opens → ENABLE cut → motors stop
              → This is a TRACE on the PCB, not a connector pin
              → The NC contact breaks the Z_EN_5V and X_EN_5V traces
```

---

## Step 12 — Status LEDs

```
  Position: Near DC jack (top edge)

  ┌────────────────────────────────────────────────────────────┐
  │                                                            │
  │  LED1 — Green — "12V Power Present"                       │
  │  ─────────────────────────────────                         │
  │                                                            │
  │  VIN_12V ──── R21 (1kΩ) ──── LED1 (green) ──── GND       │
  │                (12V - 2V)/1000Ω ≈ 10mA                     │
  │                                                            │
  │  LED2 — Red — "E-Stop Active"                             │
  │  ─────────────────────────────────                         │
  │                                                            │
  │  ESTOP_IN ──── R22 (330Ω) ──── LED2 (red) ──── GND       │
  │                                                            │
  │  LED3 — Yellow — "Step Activity"                          │
  │  ─────────────────────────────────                         │
  │                                                            │
  │  Z_STEP_5V ─── R23 (330Ω) ─── LED3 (yellow) ─── GND      │
  │                (blinks when Z motor receives steps)        │
  │                                                            │
  └────────────────────────────────────────────────────────────┘
```

---

## Complete Board Top-Down Layout

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     MbW LATHE HAT PCB                               │
  │                    (65mm × 56mm, Top View)                          │
  │                                                                     │
  │  ┌───────────────────────────────────────────────────────────────┐  │
  │  │  TOP EDGE — Power Area                                        │  │
  │  │                                                               │  │
  │  │  ┌──────┐  ┌────┐  ┌────┐  ┌────┐                            │  │
  │  │  │DC Jack│  │MP2307│ │AP2112│  LED1(Grn)                      │  │
  │  │  │ J17  │  │ U3  │  │ U4  │  LED2(Red)                       │  │
  │  │  └──────┘  └────┘  └────┘  LED3(Yel)                         │  │
  │  │   F1,D8,C7,C8  D9,L1,C9,C10,C11  C12,C13,C14                 │  │
  │  │                                                               │  │
  │  │  OR-ing: D11(buck→5V0) D12(RPi→5V0)                          │  │
  │  │          D14(LDO→3V3)   D15(RPi→3V3)                          │  │
  │  │  Bulk:   C5(10µF on 5V0)  C6(10µF on 3V3)                    │  │
  │  └───────────────────────────────────────────────────────────────┘  │
  │                                                                     │
  │  ┌──────────┐          ┌───────────────────┐          ┌──────────┐ │
  │  │          │          │                   │          │          │ │
  │  │  J2      │          │    74HC245 (U1)   │          │  J4      │ │
  │  │ Z ENC    │          │    TSSOP-20       │          │ Z SERVO  │ │
  │  │ JST-6    │          │    C1(100nF)      │          │ Molex-8  │ │
  │  │          │          │                   │          │          │ │
  │  ├──────────┤          ├────────┬──────────┤          ├──────────┤ │
  │  │          │          │        │          │          │          │ │
  │  │  J3      │          │  RPi GPIO Header  │          │  J5      │ │
  │  │ X ENC    │          │      (J1)         │          │ X SERVO  │ │
  │  │ JST-6    │          │   2×20 Male       │          │ Molex-8  │ │
  │  │          │          │                   │          │          │ │
  │  └──────────┘          └────────┴──────────┘          ├──────────┤ │
  │          R1-R4                  │                     │  J6      │ │
  │                                 │                     │SPINDLE   │ │
  │                                 │                     │ JST-3    │ │
  │                                 │                     ├──────────┤ │
  │                                 │                     │  J7      │ │
  │                                 │                     │   POT    │ │
  │                                 │                     │  JST-3   │ │
  │                                 │                  ┌──┴──────────┤ │
  │                                 │                  │             │ │
  │                                 │          ┌───────┴┐            │ │
  │                                 │          │ ADS1015│            │ │
  │                                 │          │  (U2)  │            │ │
  │                                 │          └────────┘            │ │
  │  └─────────────────────────────┴─────────────────────────────────┘ │
  │                                                                     │
  │  ┌───────────────────────────────────────────────────────────────┐  │
  │  │  BOTTOM EDGE — Screw Terminals (left → right)                 │  │
  │  │                                                               │  │
  │  │  ┌────┐┌────┐┌────┐ ┌────┐ ┌────┐┌────┐┌────┐┌────┐ ┌──────┐│  │
  │  │  │J8  ││J9  ││J10 │ │J11 │ │J12 ││J13 ││J14 ││J15 │ │ J16  ││  │
  │  │  │BTN1││BTN2││BTN3│ │HALF│ │LIMZ+││LIMZ-││LIMX+││LIMX-│ │ESTOP││  │
  │  │  │2pn ││2pn ││2pn │ │NUT │ │2pn ││2pn ││2pn ││2pn │ │ 4pn  ││  │
  │  │  └────┘└────┘└────┘ └────┘ └────┘└────┘└────┘└────┘ └──────┘│  │
  │  │                                                               │  │
  │  └───────────────────────────────────────────────────────────────┘  │
  │                                                                     │
  │  Mounting holes (M2.5):  *                   *                      │
  │                        *                       *                    │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## Complete Signal Flow (Wired Connections Summary)

```
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  POWER FLOW                                                           ║
  ╚═══════════════════════════════════════════════════════════════════════╝

  12V DC Jack (J17)
       │
       │ copper trace
       ▼
  F1 (1A fuse)
       │
       │ copper trace
       ▼
  VIN_12V net ─────────────────────────────────────┬────────────────────┐
       │                                           │                    │
       ├─→ D8 (TVS to GND)                        │                    │
       ├─→ C7 (10µF to GND)                       │                    │
       ├─→ C8 (100nF to GND)                      │                    │
       │                                           │                    │
       ├───────────────────────────────────────────┤                    │
       │                                           │                    │
  ┌────┴────┐                              ┌──────┴──────┐              │
  │  MP2307 │                              │   AP2112    │              │
  │   (U3)  │                              │   (U4)      │              │
  └────┬────┘                              └──────┬──────┘              │
       │ 5V0_BUCK                                 │ 3V3_REG             │
       │                                          │                     │
       ├─→ D11 anode                              ├─→ D14 anode         │
       │                                          │                     │
  RPi Pin 2 (5V) ──→ D12 anode              RPi Pin 1 (3.3V) ──→ D15 anode
       │                                          │                     │
       └──────┬──────┘                            └──────┬──────┘        │
              │                                          │               │
              ▼                                          ▼               │
             5V0 rail                                   3V3 rail          │
              │                                          │               │
              ├─→ 74HC245 VCC                            ├─→ ADS1015 VDD │
              ├─→ Servo connectors (Pin 6)               ├─→ Encoders    │
              ├─→ Pot J7 Pin 1                           ├─→ Pull-ups    │
              ├─→ Spindle J6 Pin 1                       ├─→ I2C pull-ups│
              └─→ C5 (10µF to GND)                       └─→ C6 (10µF to GND)


  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  MOTOR SIGNAL FLOW (trace-by-trace)                                   ║
  ╚═══════════════════════════════════════════════════════════════════════╝

  Z-AXIS:
  J1 Pin 11 (GPIO 17) ──copper trace──→ 74HC245 Pin 1 (A1)
  74HC245 Pin 12 (B1) ──copper trace──→ R5 (100Ω) ──→ J4 Pin 1 (STEP)
  D1 (TVS) from Z_STEP_5V trace to GND

  J1 Pin 13 (GPIO 27) ──copper trace──→ 74HC245 Pin 2 (A2)
  74HC245 Pin 13 (B3) ──copper trace──→ R6 (100Ω) ──→ J4 Pin 2 (DIR)
  D2 (TVS) from Z_DIR_5V trace to GND

  J1 Pin 15 (GPIO 22) ──copper trace──→ 74HC245 Pin 3 (A3)
  74HC245 Pin 14 (B3) ──copper trace──→ J4 Pin 3 (EN)
  D3 (TVS) from Z_EN_5V trace to GND

  X-AXIS:
  J1 Pin 18 (GPIO 24) ──copper trace──→ 74HC245 Pin 4 (A4)
  74HC245 Pin 15 (B4) ──copper trace──→ R7 (100Ω) ──→ J5 Pin 1 (STEP)
  D4 (TVS) from X_STEP_5V trace to GND

  J1 Pin 16 (GPIO 23) ──copper trace──→ 74HC245 Pin 5 (A5)
  74HC245 Pin 16 (B5) ──copper trace──→ R8 (100Ω) ──→ J5 Pin 2 (DIR)
  D5 (TVS) from X_DIR_5V trace to GND

  J1 Pin 22 (GPIO 25) ──copper trace──→ 74HC245 Pin 6 (A6)
  74HC245 Pin 17 (B6) ──copper trace──→ J5 Pin 3 (EN)
  D6 (TVS) from X_EN_5V trace to GND


  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  ALL GPIO TRACE ROUTING (J1 pin → destination)                        ║
  ╚═══════════════════════════════════════════════════════════════════════╝

  J1 Pin  3 (GPIO 2)  ──→ I2C_SDA ──→ ADS1015 Pin 1  [+ R22 4.7kΩ pull-up to 3V3]
  J1 Pin  5 (GPIO 3)  ──→ I2C_SCL ──→ ADS1015 Pin 2  [+ R23 4.7kΩ pull-up to 3V3]
  J1 Pin  7 (GPIO 4)  ──→ HALF_NUT_IN ──→ J11 Pin 1  [+ R15 10kΩ pull-down to GND]
  J1 Pin 11 (GPIO 17) ──→ 74HC245 Pin 1 (A1)
  J1 Pin 13 (GPIO 27) ──→ 74HC245 Pin 2 (A2)
  J1 Pin 15 (GPIO 22) ──→ 74HC245 Pin 3 (A3)
  J1 Pin 16 (GPIO 23) ──→ 74HC245 Pin 5 (A5)
  J1 Pin 18 (GPIO 24) ──→ 74HC245 Pin 4 (A4)
  J1 Pin 22 (GPIO 25) ──→ 74HC245 Pin 6 (A6)
  J1 Pin 23 (GPIO 11) ──→ LIM_X_MINUS_IN ──→ J15 Pin 1  [+ R19 10kΩ pull-up to 3V3]
  J1 Pin 24 (GPIO 8)  ──→ LIM_X_PLUS_IN  ──→ J14 Pin 1  [+ R18 10kΩ pull-up to 3V3]
  J1 Pin 26 (GPIO 7)  ──→ LIM_Z_MINUS_IN ──→ J13 Pin 1  [+ R17 10kΩ pull-up to 3V3]
  J1 Pin 29 (GPIO 5)  ──→ Z_ENC_A ──→ J2 Pin 3         [+ R1 10kΩ pull-up to 3V3]
  J1 Pin 31 (GPIO 6)  ──→ Z_ENC_B ──→ J2 Pin 4         [+ R2 10kΩ pull-up to 3V3]
  J1 Pin 32 (GPIO 12) ──→ SPINDLE_IN (from R10/R11 voltage divider)
  J1 Pin 33 (GPIO 13) ──→ X_ENC_A ──→ J3 Pin 3         [+ R3 10kΩ pull-up to 3V3]
  J1 Pin 35 (GPIO 19) ──→ X_ENC_B ──→ J3 Pin 4         [+ R4 10kΩ pull-up to 3V3]
  J1 Pin 36 (GPIO 16) ──→ LIM_Z_PLUS_IN  ──→ J12 Pin 1  [+ R16 10kΩ pull-up to 3V3]
  J1 Pin 37 (GPIO 26) ──→ BTN1_IN  ──→ J8 Pin 1        [+ R12 10kΩ pull-up to 3V3]
  J1 Pin 38 (GPIO 20) ──→ BTN2_IN  ──→ J9 Pin 1        [+ R13 10kΩ pull-up to 3V3]
  J1 Pin 40 (GPIO 21) ──→ BTN3_IN  ──→ J10 Pin 1       [+ R14 10kΩ pull-up to 3V3]

  Power/GND pins (J1):
  J1 Pin  1 (3.3V)  ──→ D15 anode ──→ 3V3 rail
  J1 Pin  2 (5V)    ──→ D12 anode ──→ 5V0 rail
  J1 Pin  4 (5V)    ──→ 5V0 rail (direct tie to Pin 2 net)
  J1 Pin 17 (3.3V)  ──→ D15 anode (same net as Pin 1)
  J1 Pin  6,9,14,20,25,30,34,39 ──→ GND plane
```

---

## Capacitor Placement Map

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  CAPACITOR — VALUE — CONNECTION — LOCATION                          │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  POWER INPUT AREA (near DC jack):                                   │
  │  C7    10µF 25V   VIN_12V → GND     Near fuse output               │
  │  C8    100nF 25V  VIN_12V → GND     Next to C7                     │
  │                                                                     │
  │  BUCK REGULATOR (around MP2307):                                    │
  │  C9    22µF 16V   5V0_BUCK → GND   Near buck output                │
  │  C10   100nF 16V  5V0_BUCK → GND   Next to C9                     │
  │  C11   100nF 16V  BOOT → SW        Directly across pins 5 and 3   │
  │                                                                     │
  │  LDO REGULATOR (around AP2112):                                     │
  │  C12   10µF 16V   VIN_12V → GND    Near LDO input (Pin 1)         │
  │  C13   10µF 6.3V  3V3_REG → GND    Near LDO output (Pin 4)        │
  │  C14   100nF 10V  3V3_REG → GND    Next to C13                    │
  │                                                                     │
  │  74HC245 (level shifter):                                           │
  │  C1    100nF 10V  Pin 20(VCC) → GND  Within 2mm of Pin 20!        │
  │                                                                     │
  │  ADS1015 (ADC):                                                     │
  │  C2    100nF 10V  Pin 9(AVDD) → Pin 10(AVSS)  Across pins!        │
  │  C3    100nF 10V  Pin 5(DVDD) → Pin 6(DVSS)   Across pins!        │
  │  C4    10µF 6.3V  3V3 → GND          Near ADS1015                 │
  │                                                                     │
  │  BULK DECOUPLING (power rails):                                     │
  │  C5    10µF 10V   5V0 → GND          Near 74HC245                 │
  │  C6    10µF 6.3V  3V3 → GND          Near GPIO header             │
  │                                                                     │
  │  TOTAL: 13 capacitors                                               │
  │                                                                     │
  │  NOTE: NO capacitors on I2C SDA/SCL lines!                         │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

---

*Corrected PCB build guide — RPi native USB-C, 12V DC jack on HAT only.*
*Updated: 2026-08-04*
