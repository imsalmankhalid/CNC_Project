---
name: mbw-lathe
description: "MbW (Machine-by-Wire) lathe control system project. Use for: understanding the lathe architecture, debugging motion control, adding features to modes (standard/threading/profile/radius), working with hardware interfaces (HAL layer), modifying the PyQt5 HMI UI, tracing potentiometer or encoder flows, adding new GPIO pins, working with the Arduino legacy firmware, or any question about the lathe control system. Keywords: lathe, servo, handwheel, encoder, potentiometer, feed rate, spindle RPM, half-nut, threading, profile, radius, DRO, motion controller, HAL, hardware interface, ADS1015, ClearPath, Teknic, Arduino Mega, Raspberry Pi, PyQt5."
argument-hint: "Describe the lathe system task or question"
user-invocable: true
---

# MbW Lathe Control System

## What It Is
Machine-by-Wire (MbW) lathe controller that converts a conventional manual lathe into a servo-assisted CNC-style machine. Handwheel input is amplified by Teknic ClearPath servo motors — the operator feels the handwheel, but the servo does the mechanical work.

## Architecture
Two-tier system with a legacy Arduino and a new Raspberry Pi replacement:

### Raspberry Pi (New — Primary Development Target)
- **Python 3.13 + PyQt5** HMI on a 7" 800×480 touchscreen
- ~60% complete, 55/55 tests passing
- Entry point: `lathe_rpi/main.py`

### Arduino Mega 2560 (Legacy — Reference Only)
- 14 `.ino` files in `libraries (2)/Lathe_v0.5.25_alpha0.1/`
- Compiled as a single translation unit
- Use as reference for understanding original behavior

## RPi Code Structure (`lathe_rpi/`)

```
main.py                    # Entry point, logging setup
config.py                  # All machine parameters, GPIO pins, ADC config
log_setup.py               # Rotating file + console logging
demo.py                    # Desktop demo without hardware

core/
  state_manager.py         # MachineState singleton (thread-safe dataclass)
  motion_controller.py     # Handwheel → servo motion (500µs SCHED_FIFO thread)
  spindle.py               # RPM from index pulse (interrupt-driven)
  feed_calculator.py       # Potentiometer → feed rate mapping (100ms poll)
  halfnut.py               # Z-axis auto-feed when half-nut engaged (10ms poll)

hal/
  hardware_interface.py    # Abstract base class for all hardware ops
  rpi_interface.py         # pigpio backend (RPi 4)
  rpi5_interface.py        # gpiozero backend (RPi 5)
  mock_interface.py        # Desktop/testing mock

modes/
  standard_mode.py         # Mode 0: DRO + handwheel following + buttons
  threading_mode.py        # Mode 1: Thread cutting wizard (17 thread sizes)
  profile_mode.py          # Mode 3: Multi-point contour turning (10 points)
  radius_mode.py           # Mode 4: Arc/sphere turning (0.5° resolution)
  base_mode.py             # Base class for all modes

ui/
  app.py                   # QMainWindow orchestrator
  theme.py                 # Industrial dark theme stylesheets
  screens/
    main_screen.py         # DRO readout (20Hz refresh)
    mode_select_screen.py  # Mode selection
    thread_screen.py       # Threading wizard UI
    profile_screen.py      # Profile/taper UI
    radius_screen.py       # Radius/sphere UI

tests/                     # Unit tests (pytest, 55 tests)
tests/simulation.py        # Hardware simulation for UI testing
```

## Key Design Patterns

### HAL (Hardware Abstraction Layer)
- Abstract base class: `hal/hardware_interface.py`
- Implementations: `RpiInterface` (pigpio), `Rpi5Interface` (gpiozero), `MockInterface` (testing)
- All hardware access goes through the HAL — never import GPIO libraries directly in core/modes/ui code

### MachineState Singleton
- Thread-safe dataclass in `core/state_manager.py`
- Accessed via `get_state()` — returns the singleton
- Use `with state.atomic():` for multi-field updates
- Key fields: positions, feed rates, RPM, mode, limits, estop, memory slots

### Background Threads
| Thread | Rate | Purpose |
|--------|------|---------|
| MotionController | 500µs (SCHED_FIFO) | Handwheel encoder → servo step conversion |
| SpindleMonitor | Interrupt-driven | RPM from spindle index pulse |
| HalfNutController | 10ms | Z-axis auto-feed when half-nut engaged |
| FeedCalculator | 100ms | Potentiometer → feed rate mapping |

### Modes (State Machines)
All modes inherit from `BaseMode` and implement `process()` for state machine logic.

| Mode | ID | File | Description |
|------|-----|------|-------------|
| Standard (DRO) | 0 | standard_mode.py | Default, handwheel following + DRO |
| Threading | 1 | threading_mode.py | Thread cutting wizard |
| Profile (Taper) | 3 | profile_mode.py | Multi-point contour turning |
| Radius (Sphere) | 4 | radius_mode.py | Arc/sphere turning |
| Menu | 999 | — | Mode selection (transient) |

## Hardware Details

### RPi GPIO (BCM numbering)
| Signal | GPIO | Notes |
|--------|------|-------|
| Z Encoder A/B | 5/6 | gpiozero RotaryEncoder |
| X Encoder A/B | 13/19 | gpiozero RotaryEncoder |
| Spindle Index | 12 | Voltage-divided from 5V |
| Z STEP/DIR/ENABLE | 17/27/22 | Via level shifter → 5V |
| X STEP/DIR/ENABLE | 24/23/25 | Via level shifter → 5V |
| Button 1/2/3 | 26/20/21 | Active LOW, pull-up |
| Half-Nut Switch | 4 | Active HIGH, pull-down |
| Limit Z+ | 16 | NC switch, pull-up |
| Limit X+ | 8 | NC switch, pull-up |
| I2C SDA/SCL | 2/3 | ADS1015 ADC |

### Potentiometer (ADS1015 Channel A0)
- Controls Z-axis feed rate for electronic half-nut
- ADS1015 I2C ADC on channel A0 (12-bit, normalized to 0–1023)
- Mapping: 0–1023 → 12.7–1270 mm/min (0.5–50 IPM)
- Clamped: pot < 18 → min, pot > 1007 → max
- `FeedCalculator` polls at 100ms with debouncing (>5 ADC change)
- Config: `ADC_BACKEND = "ads1015"`, `ADC_POT_CHANNEL = 0`

### Motors
- Teknic ClearPath SDSK digital servos (step/dir, 800 counts/rev)
- Level shifters mandatory (3.3V → 5V TTL)

## Common Tasks

### Tracing a Signal Flow
1. **Potentiometer → Feed Rate**: `FeedCalculator._poll_loop()` → `hw.read_potentiometer()` → `_calc()` → `MachineState.feed_rate_mm` → displayed in `MainScreen` speed panel
2. **Handwheel → Motor**: `RotaryEncoder` interrupt → `MotionController` reads delta → velocity calc → `hw.z_step()/x_step()` → servo
3. **Spindle → RPM**: Index pulse on GPIO 12 → hardware interrupt → `SpindleMonitor` timestamps → RPM = 60,000,000 / Δt_µs → `MachineState.spindle_rpm`

### Adding a New GPIO Pin
1. Add `GPIO_XXX = N` in `config.py`
2. Add abstract method to `hal/hardware_interface.py`
3. Implement in `rpi_interface.py` and `rpi5_interface.py`
4. Implement in `mock_interface.py` for testing
5. Add to `MachineState` if state needs to be tracked

### Adding a New Mode
1. Create `modes/new_mode.py` inheriting from `BaseMode`
2. Assign a mode ID (avoid 0, 1, 3, 4, 999)
3. Add to `app.py` mode creation and switching logic
4. Create corresponding screen in `ui/screens/`
5. Add tests in `tests/`

### Running Tests
```bash
cd lathe_rpi
python -m pytest tests/ -v              # All unit tests
bash run_combined_tests.sh              # Integration tests
```

### Running the Application
```bash
cd lathe_rpi
python main.py                          # On RPi (fullscreen)
python main.py --windowed               # Desktop testing
```

## Configuration (`config.py`)
All machine parameters are in `config.py`. Key sections:
- Z/X axis mechanics (pulley teeth, screw pitch, handwheel ratios)
- Feed rate limits (FEED_RATE_MIN_MM, FEED_RATE_MAX_MM)
- Spindle limits (SPNDL_RPM_MIN, SPNDL_RPM_MAX)
- GPIO pin assignments
- ADC backend configuration
- Limit switch settings
- Logging configuration

## Important Files to Read First
- `config.py` — all parameters and pin assignments
- `core/state_manager.py` — shared state structure
- `hal/hardware_interface.py` — hardware API contract
- `ui/app.py` — application orchestration
- `modes/standard_mode.py` — default mode behavior
