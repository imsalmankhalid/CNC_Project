#!/usr/bin/env python3
"""
Encoder-driven dual-motor control (electronic gearbox model).

This mirrors the step-calculation approach used by the Arduino Mega lathe
firmware (see libraries (2)/Lathe_v0.5.25_alpha0.1, files 20_HandWh_Z.ino
and 21_HandWh_X.ino):

    * The motor POSITION follows the encoder POSITION through a fixed
      ratio "CountAdjust" (motor counts per encoder count).  This is an
      electronic gearbox / handwheel behaviour, not a speed match.
    * For every encoder count the required motor steps are calculated as
      encoder_counts * CountAdjust and accumulated as a target position.
    * A per-axis stepper thread emits exactly the pulses needed to reach
      that target.  The step frequency is derived from how many steps are
      still pending (the "buffer"), so the faster the encoder is turned
      the faster the motor runs - exactly like the Arduino zCalcVel logic.

Axis / encoder mapping:
    * Encoder 1 (enc1)  ->  X-axis motor
    * Encoder 2 (enc2)  ->  Z-axis motor

A potentiometer on channel A0 of an ADS1015 ADC scales the Z-axis speed
(0 V -> stopped, full scale -> full speed).  It only changes how fast the
Z motor chases its target; it never changes the target itself, so no
steps are lost.

Ratios come from the Arduino firmware mechanics:
    xCountAdjust = (xHandwheel/xEncCntPerRev)/(xPitch/xMtrCntPerRev) = 0.4
    zCountAdjust = (zHandwheel/zEncCntPerRev)/(zPitch/zMtrCntPerRev) = 1.6

All pins use BCM (GPIO) numbering.
"""

import threading
import time
from time import perf_counter

from gpiozero import Device, DigitalOutputDevice, RotaryEncoder
from gpiozero.pins.lgpio import LGPIOFactory

# Bind gpiozero to the lgpio backend on the header gpiochip.
# gpiochip0 (pinctrl-rp1) is the 40-pin header on current Pi 5 kernels.
Device.pin_factory = LGPIOFactory(chip=0)

# ---------------------------------------------------------------------------
# Pin configuration (BCM numbering) - edit to match your wiring
# ---------------------------------------------------------------------------
# X-axis motor
X_STEP_PIN = 24
X_DIR_PIN = 23
X_EN_PIN = 25

# Z-axis motor
Z_STEP_PIN = 17
Z_DIR_PIN = 27
Z_EN_PIN = 22

# Encoder 1 -> X-axis
ENC1_A_PIN = 13
ENC1_B_PIN = 19

# Encoder 2 -> Z-axis
ENC2_A_PIN = 5
ENC2_B_PIN = 6

# ---------------------------------------------------------------------------
# Electronic-gearbox ratios (motor counts per encoder count)
# ---------------------------------------------------------------------------
# From the Arduino firmware:
#   xCountAdjust = 0.4  -> 0.4 motor counts per encoder count
#   zCountAdjust = 1.6  -> 1.6 motor counts per encoder count
# If your gpiozero encoder yields a different counts-per-rev (gpiozero
# counts every quadrature edge), scale these until 1 handwheel rev gives
# the expected linear travel.
X_COUNT_ADJUST = 0.4
Z_COUNT_ADJUST = 1.6

# ---------------------------------------------------------------------------
# Motion configuration
# ---------------------------------------------------------------------------
FORWARD = 1
REVERSE = 0

# Step frequency is proportional to the pending-step backlog (buffer).
# freq = clamp(|pending| * SPEED_GAIN_HZ_PER_STEP, MIN..MAX).
# A larger gain reaches full speed with a smaller backlog (snappier).
SPEED_GAIN_HZ_PER_STEP = 400.0

# Clamp the generated step frequency to a safe range (Hz).
MIN_STEP_FREQ = 1000
MAX_STEP_FREQ = 20000

# Direction-setup settle time before the first pulse (seconds).
DIR_SETTLE_S = 0.000005      # 5 us, ClearPath min setup time
ENABLE_SETTLE_S = 0.5

# Idle sleep for a stepper thread when it has nothing to do (seconds).
IDLE_SLEEP_S = 0.001

# How often the main loop samples the encoders (seconds).
UPDATE_INTERVAL = 0.02

# Potentiometer (ADS1015 A0) scaling for the Z axis.
POT_MAX_VOLTAGE = 3.3   # set to 5.0 if the pot is wired to 5 V


def _precise_sleep(duration):
    """Sleep with sub-millisecond accuracy using a short busy-wait tail."""
    if duration <= 0:
        return
    end = perf_counter() + duration
    # Give up the CPU for the bulk of long waits, busy-wait the remainder.
    if duration > 0.002:
        time.sleep(duration - 0.001)
    while perf_counter() < end:
        pass


# ---------------------------------------------------------------------------
# Axis: electronic-gearbox stepper driven by a background thread
# ---------------------------------------------------------------------------
class MotorAxis:
    """
    Follows a target position (in motor steps) set by the main loop.

    The main loop computes the target from the encoder using CountAdjust;
    this thread emits exactly the pulses needed to reach it, at a speed
    proportional to the outstanding backlog.
    """

    def __init__(self, name, step_pin, dir_pin, en_pin):
        self.name = name
        self.step = DigitalOutputDevice(step_pin, initial_value=False)
        self.direction = DigitalOutputDevice(dir_pin,
                                             initial_value=bool(FORWARD))
        self.enable = DigitalOutputDevice(en_pin, initial_value=False)

        self._lock = threading.Lock()
        self._target = 0          # desired motor position (steps)
        self._position = 0        # current motor position (steps)
        self._speed_scale = 1.0   # 0..1 external speed limit (e.g. pot)
        self._cur_dir = FORWARD
        self._freq = 0.0          # last commanded frequency (for display)

        self._alive = True
        self._thread = threading.Thread(target=self._run, daemon=True)

    # -- public API used by the main loop ---------------------------------
    def start(self):
        self._thread.start()

    def set_enable(self, state):
        if state:
            if not self.enable.is_active:
                self.enable.on()
                time.sleep(ENABLE_SETTLE_S)
        else:
            self.enable.off()

    def set_target(self, target_steps):
        with self._lock:
            self._target = int(target_steps)

    def set_speed_scale(self, scale):
        with self._lock:
            self._speed_scale = max(0.0, min(1.0, scale))

    @property
    def status(self):
        with self._lock:
            pending = self._target - self._position
            return self._position, pending, self._freq

    def stop(self):
        self._alive = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def close(self):
        self.stop()
        self.enable.off()
        self.step.close()
        self.direction.close()
        self.enable.close()

    # -- stepper thread ----------------------------------------------------
    def _run(self):
        while self._alive:
            with self._lock:
                pending = self._target - self._position
                scale = self._speed_scale

            if pending == 0 or scale <= 0.0:
                self._freq = 0.0
                _precise_sleep(IDLE_SLEEP_S)
                continue

            # Direction from the sign of the backlog.
            new_dir = FORWARD if pending > 0 else REVERSE
            if new_dir != self._cur_dir:
                self.direction.value = 1 if new_dir == FORWARD else 0
                self._cur_dir = new_dir
                _precise_sleep(DIR_SETTLE_S)

            # Frequency proportional to backlog (Arduino zCalcVel analogue),
            # then scaled by the external speed limit (pot on Z).
            freq = abs(pending) * SPEED_GAIN_HZ_PER_STEP
            if freq < MIN_STEP_FREQ:
                freq = MIN_STEP_FREQ
            elif freq > MAX_STEP_FREQ:
                freq = MAX_STEP_FREQ
            freq *= scale
            if freq < 1.0:
                self._freq = 0.0
                _precise_sleep(IDLE_SLEEP_S)
                continue
            self._freq = freq

            half_period = 0.5 / freq

            # Emit exactly one step pulse and advance the tracked position.
            self.step.on()
            _precise_sleep(half_period)
            self.step.off()
            _precise_sleep(half_period)

            with self._lock:
                self._position += 1 if new_dir == FORWARD else -1


# ---------------------------------------------------------------------------
# Optional potentiometer (ADS1015 A0) for Z-axis speed scaling
# ---------------------------------------------------------------------------
def init_pot():
    """Return a reader callable giving a 0..1 scale, or None if unavailable."""
    try:
        import board
        from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15

        i2c = board.I2C()
        ads = ADS1015(i2c)
        chan = AnalogIn(ads, ads1x15.Pin.A0)

        last_scale = [1.0]

        def read_scale():
            # Tolerate transient I2C hiccups: keep the last good value
            # instead of crashing the control loop.
            try:
                voltage = max(0.0, min(chan.voltage, POT_MAX_VOLTAGE))
                last_scale[0] = voltage / POT_MAX_VOLTAGE
            except OSError:
                pass
            return last_scale[0]

        print("Potentiometer on A0 ready (scales Z-axis speed).")
        return read_scale
    except Exception as exc:  # noqa: BLE001 - hardware optional
        print(f"Potentiometer unavailable ({exc}); Z speed not scaled.")
        return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    print("Initializing motors and encoders...")

    x_axis = MotorAxis("X", X_STEP_PIN, X_DIR_PIN, X_EN_PIN)
    z_axis = MotorAxis("Z", Z_STEP_PIN, Z_DIR_PIN, Z_EN_PIN)

    enc1 = RotaryEncoder(ENC1_A_PIN, ENC1_B_PIN, max_steps=0)  # X
    enc2 = RotaryEncoder(ENC2_A_PIN, ENC2_B_PIN, max_steps=0)  # Z

    pot_reader = init_pot()

    # Enable both drives and zero the reference so motor 0 == encoder 0.
    x_axis.set_enable(True)
    z_axis.set_enable(True)

    x_zero = enc1.steps
    z_zero = enc2.steps

    x_axis.start()
    z_axis.start()

    print("Running. Spin the encoders to move the motors. Ctrl+C to quit.\n")

    try:
        while True:
            _precise_sleep(UPDATE_INTERVAL)

            # Motor target = encoder displacement * gearbox ratio.
            x_counts = enc1.steps - x_zero
            z_counts = enc2.steps - z_zero
            x_axis.set_target(round(x_counts * X_COUNT_ADJUST))
            z_axis.set_target(round(z_counts * Z_COUNT_ADJUST))

            # Pot scales only the Z chase speed, never the Z target.
            z_axis.set_speed_scale(pot_reader() if pot_reader else 1.0)

            x_pos, x_pending, x_freq = x_axis.status
            z_pos, z_pending, z_freq = z_axis.status

            print(
                f"\rX: enc {x_counts:>7} -> mtr {x_pos:>7} "
                f"(pend {x_pending:>5}, {x_freq:>6.0f} Hz) | "
                f"Z: enc {z_counts:>7} -> mtr {z_pos:>7} "
                f"(pend {z_pending:>5}, {z_freq:>6.0f} Hz)   ",
                end="", flush=True,
            )

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        x_axis.close()
        z_axis.close()
        enc1.close()
        enc2.close()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
