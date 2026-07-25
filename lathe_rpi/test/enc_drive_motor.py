#!/usr/bin/env python3
"""
Electronic gearbox: motor position follows encoder position at a fixed ratio,
with the gear ratio set live by a potentiometer.

Each encoder is mechanically "geared" to one ClearPath SDSK motor in
software.  For every encoder count the axis commands GEAR_RATIO motor
steps, so the motor shaft tracks the encoder shaft at a constant ratio and
in a consistent direction:

    motor_target_steps = encoder_counts * GEAR_RATIO

    * Encoder 1 (AMT103-V, GPIO 5/6)    ->  X-axis motor
          STEP=17, DIR=27, EN=22
    * Encoder 2 (AMT103-V, GPIO 13/19)  ->  Z-axis motor
          STEP=24, DIR=23, EN=25

A single potentiometer on the ADS1015 ADC (channel A0) sets the gear ratio
for BOTH axes at once.  Turning the pot up increases the ratio (more motor
movement per encoder count); turning it down decreases it.

Turning an encoder clockwise drives its motor one way; counter-clockwise
drives it the other way.  Stop turning and the motor holds position.

Uses the libraries recommended by the Raspberry Pi GPIO white paper:
gpiozero with the lgpio pin factory (the RP1 backend on the Pi 5), plus the
Adafruit ADS1x15 driver for the analog pot.
"""

import time

import board
from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15
from gpiozero import Device, DigitalOutputDevice, RotaryEncoder
from gpiozero.pins.lgpio import LGPIOFactory

# Bind gpiozero to the lgpio backend on the header gpiochip.
# gpiochip0 (pinctrl-rp1) is the 40-pin header on current Pi 5 kernels.
Device.pin_factory = LGPIOFactory(chip=0)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ENABLE_SETTLE_S = 0.5   # ClearPath needs a moment after Enable before moving
STEP_PULSE_S = 0.00005  # step pulse high/low half-period (ClearPath >= ~1us)
MAX_STEPS_PER_UPDATE = 200  # cap pulses per loop so both axes stay responsive
POLL_S = 0.001          # main loop interval

# Potentiometer -> gear ratio mapping.
POT_MAX_VOLTAGE = 3.3   # pot reference voltage (use 5.0 if wired to 5V)
RATIO_MIN = 1.0         # gear ratio at pot fully down
RATIO_MAX = 20.0        # gear ratio at pot fully up
RATIO_STEP = 0.5        # quantize ratio so it does not jitter with pot noise

FORWARD = 1
REVERSE = 0


class Potentiometer:
    """Read a pot on the ADS1015 and map it to a quantized gear ratio."""

    def __init__(self, channel=ads1x15.Pin.A0):
        i2c = board.I2C()
        self.ads = ADS1015(i2c)
        self.chan = AnalogIn(self.ads, channel)
        # Cache last good readings so a transient I2C glitch does not crash
        # or lurch the motion loop.
        self._voltage = 0.0
        self._raw = 0
        self.read()

    def read(self):
        """Sample the ADC, holding the last good value on a bus glitch."""
        try:
            self._voltage = self.chan.voltage
            self._raw = self.chan.value
        except OSError:
            pass  # keep the previous cached reading
        return self._voltage

    @property
    def voltage(self):
        return self._voltage

    @property
    def raw(self):
        return self._raw

    @property
    def fraction(self):
        """Pot position as 0.0 .. 1.0."""
        v = max(0.0, min(self._voltage, POT_MAX_VOLTAGE))
        return v / POT_MAX_VOLTAGE

    @property
    def ratio(self):
        """Gear ratio from the pot, quantized to avoid ADC jitter."""
        raw_ratio = RATIO_MIN + self.fraction * (RATIO_MAX - RATIO_MIN)
        return round(raw_ratio / RATIO_STEP) * RATIO_STEP


class GearboxAxis:
    """Follow one motor's position to one encoder at a live gear ratio."""

    def __init__(self, name, enc_a, enc_b, step_pin, dir_pin, en_pin,
                 ratio=RATIO_MIN):
        self.name = name
        self.ratio = ratio

        self.encoder = RotaryEncoder(enc_a, enc_b, max_steps=0)
        self.step = DigitalOutputDevice(step_pin, initial_value=False)
        self.direction = DigitalOutputDevice(dir_pin, initial_value=True)
        self.enable = DigitalOutputDevice(en_pin, initial_value=False)

        # Commanded motor position, in motor steps, that we have emitted.
        self.motor_position = 0
        self.current_direction = None

        # Reference origins so a live ratio change does not lurch the motor:
        #   target = motor_origin + (enc.steps - enc_origin) * ratio
        self.enc_origin = self.encoder.steps
        self.motor_origin = 0

        # Enable the drive once at start-up so it is ready to move.
        self.enable.on()
        time.sleep(ENABLE_SETTLE_S)

    def set_ratio(self, ratio):
        """Change the gear ratio, rebasing so the motor does not jump."""
        if ratio != self.ratio:
            self.enc_origin = self.encoder.steps
            self.motor_origin = self.motor_position
            self.ratio = ratio

    def _set_direction(self, direction_value):
        if direction_value != self.current_direction:
            self.direction.value = 1 if direction_value == FORWARD else 0
            self.current_direction = direction_value
            time.sleep(STEP_PULSE_S)  # let the drive latch the new direction

    def _pulse(self):
        self.step.on()
        time.sleep(STEP_PULSE_S)
        self.step.off()
        time.sleep(STEP_PULSE_S)

    def update(self):
        """Emit motor steps so the axis catches up to encoder * ratio."""
        enc_delta = self.encoder.steps - self.enc_origin
        target = self.motor_origin + int(enc_delta * self.ratio)
        error = target - self.motor_position
        if error == 0:
            return

        direction_value = FORWARD if error > 0 else REVERSE
        self._set_direction(direction_value)

        # Emit a bounded burst of pulses this cycle; the remainder is picked
        # up on later updates so the sister axis keeps getting serviced.
        n = min(abs(error), MAX_STEPS_PER_UPDATE)
        step = 1 if error > 0 else -1
        for _ in range(n):
            self._pulse()
            self.motor_position += step

    @property
    def dir_label(self):
        if self.current_direction is None:
            return "--"
        return "FWD" if self.current_direction == FORWARD else "REV"

    def cleanup(self):
        self.step.off()
        self.enable.off()


def main():
    pot = Potentiometer()
    axes = [
        GearboxAxis("X", enc_a=5, enc_b=6,
                    step_pin=17, dir_pin=27, en_pin=22),
        GearboxAxis("Z", enc_a=13, enc_b=19,
                    step_pin=24, dir_pin=23, en_pin=25),
    ]

    print("Electronic gearbox ready. One pot sets the ratio for both axes.")
    print("Spin an encoder; its motor follows. Press Ctrl+C to quit.\n")

    last_display = 0.0
    try:
        while True:
            pot.read()
            ratio = pot.ratio
            for axis in axes:
                axis.set_ratio(ratio)
                axis.update()

            # Refresh the status line ~10x per second.
            now = time.monotonic()
            if now - last_display >= 0.1:
                last_display = now
                x, z = axes
                status = (
                    f"\rPot {pot.voltage:4.2f}V ({pot.raw:>5}) "
                    f"ratio {ratio:4.1f} | "
                    f"X enc {x.encoder.steps:>6} mot {x.motor_position:>7} "
                    f"{x.dir_label} | "
                    f"Z enc {z.encoder.steps:>6} mot {z.motor_position:>7} "
                    f"{z.dir_label}   "
                )
                print(status, end="", flush=True)

            time.sleep(POLL_S)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        for axis in axes:
            axis.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
