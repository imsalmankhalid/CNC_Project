# MbW Lathe System – Raspberry Pi Edition

A complete port of the Machine-by-Wire (MbW) lathe control system from
Arduino Mega to Raspberry Pi 4, featuring a modern 7-inch touchscreen HMI,
real-time motion control via pigpio, and a full test suite that runs on any
desktop without hardware.

---

## Project Structure

```
lathe_rpi/
├── main.py                    ← Application entry point
├── config.py                  ← All user-configurable machine parameters
├── requirements.txt           ← Python dependencies
├── HARDWARE.md                ← Component list, GPIO table, wiring guide
│
├── hal/                       ← Hardware Abstraction Layer
│   ├── hardware_interface.py  ← Abstract base class (all backends must implement)
│   ├── mock_interface.py      ← Desktop/test mock (no GPIO required)
│   └── rpi_interface.py       ← Real RPi implementation using pigpio
│
├── core/                      ← Real-time motion control logic
│   ├── state_manager.py       ← Global MachineState dataclass + singleton
│   ├── motion_controller.py   ← HandWheel encoder → servo step generation
│   ├── spindle.py             ← Spindle index pulse → RPM calculation
│   ├── halfnut.py             ← Electronic feed / half-nut controller
│   └── feed_calculator.py     ← Potentiometer ADC → feed rate (mm/min, IPM)
│
├── modes/                     ← Operating modes (state machines)
│   ├── base_mode.py           ← Abstract mode base class
│   ├── standard_mode.py       ← Mode 0: DRO + handwheel + button handling
│   ├── threading_mode.py      ← Mode 1: Automated external thread cutting
│   ├── profile_mode.py        ← Mode 3: Multi-point profile/taper turning
│   └── radius_mode.py         ← Mode 4: Internal/external arc turning
│
├── ui/                        ← PyQt5 touch HMI
│   ├── theme.py               ← Industrial dark stylesheet + colour palette
│   ├── app.py                 ← Main QMainWindow + service lifecycle
│   └── screens/
│       ├── main_screen.py     ← DRO display + button bar
│       ├── mode_select_screen.py ← Large-button mode selector
│       ├── thread_screen.py   ← Threading wizard
│       ├── profile_screen.py  ← Profile wizard
│       └── radius_screen.py   ← Radius/sphere wizard
│
└── tests/                     ← pytest test suite (runs on desktop)
    ├── conftest.py            ← Shared fixtures (MockInterface, reset_state)
    ├── test_motion.py         ← Motion controller unit tests
    ├── test_halfnut.py        ← Half-nut feed tests
    ├── test_feed_calculator.py ← ADC → feed rate tests
    ├── test_spindle.py        ← RPM calculation tests
    ├── test_standard_mode.py  ← Button handling + DRO tests
    ├── test_threading_mode.py ← Threading state machine tests
    └── simulation.py          ← EncoderSimulator + SpindleSimulator helpers
```

---

## Quick Start – Desktop (Windows / macOS / Linux)

```bash
# 1. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# 2. Install dependencies (pigpio will skip on non-Linux gracefully)
pip install PyQt5 numpy pytest pytest-qt pytest-mock pytest-cov

# 3. Run the UI on the desktop (uses MockInterface automatically)
python main.py

# 4. Run the full test suite (no hardware required)
cd lathe_rpi
pytest tests/ -v
```

> **Mock mode:** On Windows or any non-RPi machine, the application
> automatically falls back to `MockInterface` (simulated hardware).
> The complete UI is functional and can be used for design/demo purposes.

---

## Quick Start – Raspberry Pi

```bash
# 1. Enable I2C on the RPi (for ADS1115 potentiometer ADC)
sudo raspi-config
# Interface Options → I2C → Enable

# 2. Install pigpiod
sudo apt-get update && sudo apt-get install -y pigpio python3-pip
sudo systemctl enable pigpiod && sudo systemctl start pigpiod

# 3. Clone / copy this project to /home/pi/lathe_rpi
pip3 install -r requirements.txt

# 4. (Optional) Calibrate config.py for your mechanical setup
nano config.py

# 5. Run
python3 main.py

# 6. Auto-start on boot
sudo cp lathe.service /etc/systemd/system/
sudo systemctl enable lathe
```

---

## Testing Without Hardware (Desktop / VM / QEMU)

All tests use `MockInterface` – zero hardware dependencies.

```bash
# Run all tests with coverage report
pytest tests/ -v --cov=. --cov-report=term-missing

# Run a specific test file
pytest tests/test_motion.py -v

# Run tests in watch mode (install pytest-watch)
ptw tests/
```

### QEMU Testing

To test on an emulated RPi environment:

```bash
# 1. Install QEMU
sudo apt-get install qemu-system-arm

# 2. Download RPi OS image and boot in QEMU
# See: https://github.com/dhruvvyas90/qemu-rpi-kernel

# 3. Inside QEMU, pigpiod will not be available for real GPIO,
#    but the mock fallback ensures the application still runs.
#    Use: LATHE_MOCK=1 python3 main.py   (forces mock mode)
```

### VM Testing (VirtualBox / VMware on Windows)

1. Create a Debian/Ubuntu 64-bit VM
2. Install Python 3.10+, PyQt5, pytest
3. Run `python main.py` → MockInterface activates automatically
4. Run `pytest tests/ -v` → all tests pass without RPi

---

## Configuration

Edit `config.py` to match your lathe's mechanical setup:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Z_SCR_PITCH` | 5.0 mm | Z lead-screw pitch |
| `Z_HANDWHEEL` | 20.0 mm | Z travel per handwheel revolution |
| `Z_ENC_CNT_PER_REV` | 2000 | Z encoder resolution |
| `Z_MTR_CNT_PER_REV` | 800 | ClearPath motor resolution (set in MSP) |
| `X_SCR_PITCH` | 2.0 mm | X lead-screw pitch |
| `SPNDL_RPM_MAX` | 2060 | Machine maximum spindle RPM |
| `FEED_RATE_MIN_MM` | 12.7 | Minimum feed (0.5 IPM) |
| `FEED_RATE_MAX_MM` | 1270 | Maximum feed (50 IPM) |
| `FULLSCREEN` | True | Set False for desktop window |

See `HARDWARE.md` for the complete GPIO pin assignment table and wiring guide.

---

## Key Architecture Decisions

### Hardware Abstraction Layer
All hardware interaction goes through `HardwareInterface`. The same code runs
on RPi (`RpiInterface` via pigpio) or desktop (`MockInterface`). Tests use
`MockInterface` exclusively – no mocking frameworks needed.

### Threading Model
| Thread | Priority | Responsibility |
|--------|----------|---------------|
| Motion Control | SCHED_FIFO max | Encoder → servo steps (500 µs loop) |
| Half-Nut Feed | Normal | Feed thread (ms-range delays suffice) |
| Feed Calculator | Normal | ADC polling (100 ms) |
| Spindle Monitor | ISR callback | Index pulse (hardware interrupt) |
| Qt UI | Main thread | 20 Hz screen refresh |

### Real-Time Performance
- **pigpio** provides hardware-timed waveform generation for step pulses (~1 µs accuracy)
- **SCHED_FIFO** scheduling for the motion thread (requires `sudo`)
- For maximum determinism on RPi 4: apply PREEMPT_RT kernel patch

---

## Arduino → RPi Feature Mapping

| Arduino Function | RPi Equivalent |
|-----------------|----------------|
| `zEnc()` / `xEnc()` | `MotionController._process_z/x_handwheel()` |
| `zMotorFeed()` | `HalfNutController._feed_loop()` |
| `spindIndex()` / `calcSpeed()` | `SpindleMonitor._update_rpm()` |
| `potentiometer()` / `calcFeed()` | `FeedCalculator._calc()` |
| `stdButtons()` | `StandardMode._poll_buttons()` |
| `extThrdSetup()` / `extThrdMove()` | `ThreadingMode.confirm()` / `_run_thread_pass()` |
| `taperSetup()` / `tprMove()` | `ProfileMode.confirm()` / `_run_profile()` |
| `arcSetup()` / `arcMove()` | `RadiusMode.confirm()` / `_run_arc()` |
| `displayLcdBasicsXZ()` | `MainScreen._refresh()` |
| 4×20 LCD | 7" 800×480 PyQt5 Touch HMI |

---

## Safety Notes

1. **Hard-wire the E-Stop** into the ClearPath ENABLE line – do not rely solely on software.
2. **Level shifters are mandatory** for STEP/DIR/ENABLE signals (3.3 V RPi → 5 V ClearPath).
3. **Test at low feed rates first** before enabling maximum IPM.
4. All limit switch handling cuts motion in software AND the UI shows a persistent indicator.

---

## License

Open source – based on the original MbW project by Rob Wade (WadeODesign LLC).
RPi port developed as part of the MbW System Upgrade project.
