#!/usr/bin/env python3
"""
Combined Hardware Test Suite for Lathe RPi
Includes: Encoder, GPIO Output, Motor, Switch, GPIO Monitor, I2C ADS1115, I2C ADS1015
"""

import time
import sys


# ─────────────────────────────────────────────
# 1. Encoder Test  (enc_tes.py)
# ─────────────────────────────────────────────
def test_encoder():
    """AMT103-V Rotary Encoders on GPIO 13/19 and 5/6."""
    try:
        from gpiozero import RotaryEncoder
    except ImportError:
        print("gpiozero not available.")
        return

    # Encoder pins
    PIN_A1 = 13
    PIN_B1 = 19
    PIN_A2 = 5
    PIN_B2 = 6

    print("Initializing AMT103-V Encoders...")
    print(f"Encoder1 -> A: GPIO {PIN_A1}, B: GPIO {PIN_B1}")
    print(f"Encoder2 -> A: GPIO {PIN_A2}, B: GPIO {PIN_B2}")

    enc1 = RotaryEncoder(PIN_A1, PIN_B1, max_steps=0)
    enc2 = RotaryEncoder(PIN_A2, PIN_B2, max_steps=0)

    print("Encoders ready! Spin the shafts... (Press Ctrl+C to exit)\n")

    last1 = None
    last2 = None

    try:
        while True:
            v1 = enc1.steps
            v2 = enc2.steps

            out = []

            if v1 != last1:
                d1 = "Initialized" if last1 is None else ("CW ↻" if v1 > last1 else "CCW ↺")
                out.append(f"Enc1: {v1:<6} | {d1}")
                last1 = v1

            if v2 != last2:
                d2 = "Initialized" if last2 is None else ("CW ↻" if v2 > last2 else "CCW ↺")
                out.append(f"Enc2: {v2:<6} | {d2}")
                last2 = v2

            if out:
                print("  ".join(out))

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nEncoder test stopped.")


# ─────────────────────────────────────────────
# 2. GPIO Output Test  (gpio_test.py)
# ─────────────────────────────────────────────
def test_gpio_output():
    """Toggle GPIO 22, 17, 27 outputs."""
    try:
        from gpiozero import DigitalOutputDevice
    except ImportError:
        print("gpiozero not available.")
        return

    gpio  = DigitalOutputDevice(22)
    gpio2 = DigitalOutputDevice(17)
    gpio3 = DigitalOutputDevice(27)

    print("GPIO Output Test — pins 22, 17, 27")
    print("Enter 0 or 1 to set state. Ctrl+C to exit.\n")

    try:
        while True:
            try:
                vol = int(input("Enter GPIO state (0/1): "))
                if vol not in (0, 1):
                    print("Please enter 0 or 1.")
                    continue
                gpio.value  = vol
                gpio2.value = vol
                gpio3.value = vol
            except ValueError:
                print("Invalid input.")
    except KeyboardInterrupt:
        print("\nGPIO output test stopped.")


# ─────────────────────────────────────────────
# 3. Motor (ClearPath) Test  (motor_test.py)
# ─────────────────────────────────────────────
def test_motor():
    """ClearPath stepper motor — Step/Dir/Enable on GPIO 17/27/22."""
    try:
        from gpiozero import DigitalOutputDevice
    except ImportError:
        print("gpiozero not available.")
        return

    import threading

    STEP_PIN  = 17
    DIR_PIN   = 27
    EN_PIN    = 22
    STEP_FREQ = 500  # steps/sec

    step      = DigitalOutputDevice(STEP_PIN)
    direction = DigitalOutputDevice(DIR_PIN)
    enable    = DigitalOutputDevice(EN_PIN)

    running      = False
    pulse_thread = None

    def pulse_generator():
        half_period = 1 / (STEP_FREQ * 2)
        while running:
            step.on()
            time.sleep(half_period)
            step.off()
            time.sleep(half_period)

    def start_motion(forward=True):
        nonlocal running, pulse_thread
        stop_motion()
        direction.value = 1 if forward else 0
        running = True
        pulse_thread = threading.Thread(target=pulse_generator, daemon=True)
        pulse_thread.start()

    def stop_motion():
        nonlocal running
        running = False
        step.off()

    def run_for_seconds(forward, seconds):
        start_motion(forward)
        time.sleep(seconds)
        stop_motion()

    try:
        while True:
            print("\n=== CLEARPATH TEST ===")
            print("1. Forward 5 sec")
            print("2. Reverse 5 sec")
            print("3. Continuous Forward")
            print("4. Continuous Reverse")
            print("5. Enable")
            print("6. Disable")
            print("7. Stop")
            print("8. Quit")

            choice = input("> ")

            if choice == "1":
                run_for_seconds(True, 5)
            elif choice == "2":
                run_for_seconds(False, 5)
            elif choice == "3":
                start_motion(True)
            elif choice == "4":
                start_motion(False)
            elif choice == "5":
                enable.on()
                print("Enabled")
            elif choice == "6":
                enable.off()
                print("Disabled")
            elif choice == "7":
                stop_motion()
                print("Stopped")
            elif choice == "8":
                stop_motion()
                break

    except KeyboardInterrupt:
        stop_motion()
        print("\nMotor test stopped.")


# ─────────────────────────────────────────────
# 4. Switch / Button Test  (sw_test.py)
# ─────────────────────────────────────────────
def test_switch():
    """Monitor button press on GPIO 16 (active-low, pull-up)."""
    try:
        from gpiozero import Button
        from signal import pause
    except ImportError:
        print("gpiozero not available.")
        return

    PIN = 16
    press_count = 0

    switch = Button(PIN, pull_up=True)

    def pressed():
        nonlocal press_count
        press_count += 1
        print(f"Switch pressed: {press_count}")

    switch.when_pressed = pressed

    print("Monitoring GPIO 16 — Press Ctrl+C to exit.")

    try:
        pause()
    except KeyboardInterrupt:
        print("\nSwitch test stopped.")


# ─────────────────────────────────────────────
# 5. GPIO Monitor via gpiod  (test_c3.py)
# ─────────────────────────────────────────────
def test_gpio_monitor():
    """Read GPIO line 12 via gpiod and count INACTIVE transitions."""
    try:
        import gpiod
    except ImportError:
        print("gpiod not available.")
        return

    LINE = 12

    print(f"Monitoring /dev/gpiochip0 line {LINE} — Press Ctrl+C to exit.\n")

    try:
        with gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="gpio-monitor",
            config={LINE: gpiod.LineSettings()},
        ) as request:
            count = 0
            while True:
                value = request.get_value(LINE)
                if value == gpiod.line.Value.INACTIVE:
                    count += 1
                    print(count)
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nGPIO monitor test stopped.")


# ─────────────────────────────────────────────
# 6. I2C ADS1115 Test  (test_i2c.py)
# ─────────────────────────────────────────────
def test_ads1115():
    """Read potentiometer on ADS1115 A0 and display a voltage bar."""
    try:
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
    except ImportError:
        print("adafruit_ads1x15 / board / busio not available.")
        return

    def create_bar(voltage, max_voltage=3.3, bar_length=30):
        voltage = max(0.0, min(voltage, max_voltage))
        percent = (voltage / max_voltage) * 100
        filled  = int(round(bar_length * voltage / max_voltage))
        bar     = "█" * filled + "-" * (bar_length - filled)
        return f"[{bar}] {percent:5.1f}% ({voltage:.3f}V)"

    try:
        i2c  = busio.I2C(board.SCL, board.SDA)
        ads  = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P0)

        print("Reading potentiometer on ADS1115 A0 — Press Ctrl+C to exit.\n")

        while True:
            print(f"\r{create_bar(chan.voltage)}", end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nADS1115 test stopped.")
    except Exception as e:
        print(f"\nError: {e}")


# ─────────────────────────────────────────────
# 7. I2C ADS1015 Test  (test2.py)
# ─────────────────────────────────────────────
def test_ads1015():
    """Read potentiometer on ADS1015 A0 with raw value and voltage bar."""
    try:
        import board
        from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15
    except ImportError:
        print("adafruit_ads1x15 / board not available.")
        return

    BAR_LENGTH  = 30
    MAX_VOLTAGE = 3.3

    try:
        i2c  = board.I2C()
        ads  = ADS1015(i2c)
        chan = AnalogIn(ads, ads1x15.Pin.A0)

        print("Reading ADS1015 A0 — Press Ctrl+C to exit.\n")

        while True:
            voltage    = chan.voltage
            raw_val    = chan.value
            safe_v     = max(0.0, min(voltage, MAX_VOLTAGE))
            filled     = int(round(BAR_LENGTH * safe_v / MAX_VOLTAGE))
            bar        = "█" * filled + "-" * (BAR_LENGTH - filled)
            output     = f"\rRaw: {raw_val:>5} | V: {voltage:>5.3f}V [{bar}]"
            print(output, end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nADS1015 test stopped.")


# ─────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────
TESTS = {
    "1": ("Encoder (AMT103-V) — GPIO 13/19 and 5/6",          test_encoder),
    "2": ("GPIO Output — GPIO 22/17/27",               test_gpio_output),
    "3": ("Motor (ClearPath) — Step/Dir/Enable",       test_motor),
    "4": ("Switch / Button — GPIO 16",                 test_switch),
    "5": ("GPIO Monitor (gpiod) — line 12",            test_gpio_monitor),
    "6": ("I2C ADS1115 — potentiometer on A0",         test_ads1115),
}


def main():
    while True:
        print("\n=== Lathe RPi Hardware Test Suite ===")
        for key, (label, _) in TESTS.items():
            print(f"  {key}. {label}")
        print("  q. Quit")

        choice = input("\nSelect test: ").strip().lower()

        if choice == "q":
            print("Exiting.")
            sys.exit(0)
        elif choice in TESTS:
            print(f"\n--- Running: {TESTS[choice][0]} ---\n")
            TESTS[choice][1]()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
