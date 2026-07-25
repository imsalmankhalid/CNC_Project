#!/usr/bin/env python3
"""
Teknic ClearPath SDSK step/direction test - gpiozero edition.

This version uses the libraries recommended in the official Raspberry Pi
white paper "GPIO Usage on Raspberry Pi Devices":

    * gpiozero  - the recommended high-level Python GPIO library.
    * lgpio     - used as gpiozero's underlying "pin factory", the
                  suggested backend for the Raspberry Pi 5 (RP1).

On current Raspberry Pi OS the 40-pin header is exposed as gpiochip0
(pinctrl-rp1), confirmed with `gpiodetect`, so we bind the lgpio factory
to chip 0 exactly as the white paper illustrates.

The STEP pin is driven with a gpiozero PWMOutputDevice: setting a 50%
duty cycle at the desired frequency produces the continuous step-pulse
train the ClearPath expects, and the pin factory handles the timing.

Wiring (BCM numbering):
    STEP_PIN = 23  -> ClearPath Input B (Step)
    DIR_PIN  = 24  -> ClearPath Input A (Direction)
    EN_PIN   = 25  -> ClearPath Enable
"""

import time

from gpiozero import Device, PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

# Bind gpiozero to the lgpio backend on the header gpiochip.
# gpiochip0 (pinctrl-rp1) is the 40-pin header on current Pi 5 kernels.
Device.pin_factory = LGPIOFactory(chip=0)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
STEP_PIN = 24
DIR_PIN = 23
EN_PIN = 25

#STEP_PIN = 17
#DIR_PIN =  27
#EN_PIN =   22

STEP_FREQ = 5000    # step pulses per second (Hz)
STEP_DUTY = 0.5     # duty cycle of the step pulse (0.5 = symmetric)
MOVE_SECONDS = 5    # duration for the timed forward/reverse moves

FORWARD = 1
REVERSE = 0

# ClearPath needs a moment after Enable is asserted before it will move.
ENABLE_SETTLE_S = 0.5

# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------
# initial_value=0 -> STEP idle low; PWM starts only when we set .value.
step = PWMOutputDevice(STEP_PIN, frequency=STEP_FREQ, initial_value=0)
direction = DigitalOutputDevice(DIR_PIN, initial_value=bool(FORWARD))
enable = DigitalOutputDevice(EN_PIN, initial_value=False)

running = False
current_direction = FORWARD


# ---------------------------------------------------------------------------
# Motion helpers
# ---------------------------------------------------------------------------
def set_enable(state):
    if state:
        enable.on()
        time.sleep(ENABLE_SETTLE_S)
    else:
        enable.off()
    print("Motor ENABLED" if state else "Motor DISABLED")


def set_direction(direction_value):
    global current_direction
    current_direction = direction_value
    direction.value = 1 if direction_value == FORWARD else 0


def start_motion(direction_value):
    """Begin a continuous step-pulse train via PWM."""
    global running
    if not enable.is_active:
        set_enable(True)
    stop_motion()
    set_direction(direction_value)
    step.frequency = STEP_FREQ
    step.value = STEP_DUTY          # start the pulse train
    running = True
    print("Running", "FORWARD" if direction_value == FORWARD else "REVERSE",
          f"@ {STEP_FREQ} Hz")


def stop_motion():
    global running
    step.value = 0                  # duty 0 -> pulses stop, pin idles low
    running = False
    enable.off()


def move_for_seconds(direction_value, seconds):
    start_motion(direction_value)
    time.sleep(seconds)
    stop_motion()
    print("Move complete")


def toggle_direction():
    new_dir = REVERSE if current_direction == FORWARD else FORWARD
    set_direction(new_dir)
    print("Direction now:", "FORWARD" if new_dir == FORWARD else "REVERSE")


def cleanup():
    stop_motion()
    enable.off()



# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
MENU = """
=== CLEARPATH SDSK TEST (gpiozero + lgpio) ===
1. Forward {sec} sec
2. Reverse {sec} sec
3. Continuous Forward
4. Continuous Reverse
5. Enable motor
6. Disable motor
7. Stop
8. Toggle direction
9. Set step frequency (Hz)
0. Quit
""".format(sec=MOVE_SECONDS)


def main():
    global STEP_FREQ
    try:
        while True:
            print(MENU)
            print(f"[state] enabled={enable.is_active} running={running} "
                  f"freq={STEP_FREQ}Hz "
                  f"dir={'FWD' if current_direction == FORWARD else 'REV'}")
            choice = input("> ").strip()

            if choice == "1":
                move_for_seconds(FORWARD, MOVE_SECONDS)
            elif choice == "2":
                move_for_seconds(REVERSE, MOVE_SECONDS)
            elif choice == "3":
                set_enable(True)
                start_motion(FORWARD)
            elif choice == "4":
                set_enable(True)
                start_motion(REVERSE)
            elif choice == "5":
                set_enable(True)
            elif choice == "6":
                stop_motion()
                set_enable(False)
            elif choice == "7":
                stop_motion()
                print("Stopped")
            elif choice == "8":
                toggle_direction()
            elif choice == "9":
                try:
                    STEP_FREQ = max(1, int(input("New frequency (Hz): ")))
                    if running:
                        start_motion(current_direction)
                    print("Frequency set to", STEP_FREQ, "Hz")
                except ValueError:
                    print("Invalid number")
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
