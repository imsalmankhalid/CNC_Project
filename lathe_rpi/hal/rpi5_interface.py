"""
Raspberry Pi 5 Hardware Interface – uses gpiozero and native drivers for Pi 5 compatibility.

This back-end bypasses pigpio (which is incompatible with the RP1 on Pi 5)
and uses the modern python-gpiod/gpiozero libraries for GPIO and 
Adafruit Blinka for the I2C ADS1115 ADC.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Callable, Dict

import config as cfg
from .hardware_interface import HardwareInterface

try:
    from gpiozero import RotaryEncoder, Button, OutputDevice, Device
    from gpiozero.pins.lgpio import LGPIOFactory
    _GPIOZERO_AVAILABLE = True
except ImportError:
    _GPIOZERO_AVAILABLE = False


# ── Logging ─────────────────────────────────────────────────────────────────
# Debug logging is controlled by cfg.DEBUG_HAL or the LATHE_DEBUG_HAL env var.
# It mirrors the diagnostics printed by the validated test/enc_drive_motor.py
# so wiring can be checked against the on-screen values.
log = logging.getLogger("hal.rpi5")


def _debug_enabled() -> bool:
    if os.environ.get("LATHE_DEBUG_HAL", "").strip() in ("1", "true", "True"):
        return True
    return bool(getattr(cfg, "DEBUG_HAL", False))


class Rpi5Interface(HardwareInterface):
    """Real hardware implementation for Raspberry Pi 5 using gpiozero.

    Pin assignments, step timing and the ADS1015 potentiometer read path are
    kept in sync with test/enc_drive_motor.py, which was validated against the
    physical lathe hardware.
    """

    # Step pulse timing – matches the validated gearbox test (50 µs half-period
    # is comfortably above the ClearPath SDSK minimum and reliable under the
    # software-timed loop on the Pi 5).
    _STEP_PULSE_S = 50e-6
    _STEP_GAP_S   = 50e-6
    # ClearPath needs a moment after Enable before it will accept motion, and a
    # brief settle after a DIR change before the first STEP edge.
    _ENABLE_SETTLE_S = 0.5
    _DIR_SETTLE_S    = 50e-6

    def __init__(self) -> None:
        if not _GPIOZERO_AVAILABLE:
            raise RuntimeError(
                "gpiozero is not installed. Install it with: pip install gpiozero"
            )
        # Bind gpiozero to the lgpio backend on the 40-pin header gpiochip,
        # exactly as the validated test does.  gpiochip0 (pinctrl-rp1) is the
        # header on current Pi 5 kernels.
        try:
            if not isinstance(Device.pin_factory, LGPIOFactory):
                Device.pin_factory = LGPIOFactory(chip=0)
        except Exception as exc:  # pragma: no cover - depends on kernel/chip
            log.warning("Could not bind LGPIOFactory(chip=0): %s", exc)

        self._debug = _debug_enabled()
        if self._debug:
            # Ensure logging goes to the console/file even when this HAL is used
            # standalone (outside main.py).  No-op if already configured.
            try:
                from log_setup import setup_logging
                setup_logging()
            except Exception:
                if not logging.getLogger().handlers:
                    logging.basicConfig(level=logging.DEBUG)
            log.setLevel(logging.DEBUG)
        self._start_time_ns: int = 0
        self._z_dec: RotaryEncoder | None = None
        self._x_dec: RotaryEncoder | None = None
        
        # Output devices
        self._z_step_pin: OutputDevice | None = None
        self._z_dir_pin: OutputDevice | None = None
        self._z_enable_pin: OutputDevice | None = None
        
        self._x_step_pin: OutputDevice | None = None
        self._x_dir_pin: OutputDevice | None = None
        self._x_enable_pin: OutputDevice | None = None

        # Input devices
        self._btns: Dict[int, Button] = {}
        self._halfnut_btn: Button | None = None
        self._limits: Dict[tuple[str, str], Button] = {}
        self._spindle_pin: Button | None = None

        # ADS1015/ADS1115 handle (optional)
        self._ads = None
        self._ads_chan = None
        # Cache the last good pot reading so a transient I2C glitch does not
        # crash the feed loop or make the feed rate jump (mirrors the test).
        self._pot_last: int = 512
        self._pot_last_log: int = -1
        # Last encoder values logged, so debug output only fires on change.
        self._z_enc_log: int | None = None
        self._x_enc_log: int | None = None
        # Periodic encoder heartbeat: log the live value even when it is not
        # changing, so a stuck/unwired encoder is visible instead of silent.
        self._enc_hb_interval_s = 1.0
        self._z_enc_hb_next = 0.0
        self._x_enc_hb_next = 0.0

    # ── Life-cycle ──────────────────────────────────────────────────────────

    def initialise(self) -> None:
        self._start_time_ns = time.monotonic_ns()

        # Encoders (quadrature, active-low pullups)
        self._z_dec = RotaryEncoder(cfg.GPIO_Z_ENC_A, cfg.GPIO_Z_ENC_B, max_steps=0)
        self._x_dec = RotaryEncoder(cfg.GPIO_X_ENC_A, cfg.GPIO_X_ENC_B, max_steps=0)

        # Servo outputs
        self._z_step_pin   = OutputDevice(cfg.GPIO_Z_STEP, initial_value=False)
        self._z_dir_pin    = OutputDevice(cfg.GPIO_Z_DIR, initial_value=False)
        self._z_enable_pin = OutputDevice(cfg.GPIO_Z_ENABLE, initial_value=False)

        self._x_step_pin   = OutputDevice(cfg.GPIO_X_STEP, initial_value=False)
        self._x_dir_pin    = OutputDevice(cfg.GPIO_X_DIR, initial_value=False)
        self._x_enable_pin = OutputDevice(cfg.GPIO_X_ENABLE, initial_value=False)

        # Buttons (active-LOW, internal pull-up)
        for num, pin in ((1, cfg.GPIO_BTN_1), (2, cfg.GPIO_BTN_2), (3, cfg.GPIO_BTN_3)):
            self._btns[num] = Button(pin, pull_up=True)

        # Half-nut switch (active-HIGH, pull-down)
        self._halfnut_btn = Button(cfg.GPIO_HALFNUT, pull_up=False)

        # Limit switches (normally-closed, active-HIGH when triggered, internal pull-up)
        # NC wiring: switch closed (not triggered) → pin LOW → is_pressed=True
        #            switch opens (triggered)     → pin HIGH → is_pressed=False
        self._limits[("Z", "+")] = Button(cfg.GPIO_LIM_Z_PLUS, pull_up=True)
        self._limits[("Z", "-")] = Button(cfg.GPIO_LIM_Z_MINUS, pull_up=True)
        self._limits[("X", "+")] = Button(cfg.GPIO_LIM_X_PLUS, pull_up=True)
        self._limits[("X", "-")] = Button(cfg.GPIO_LIM_X_MINUS, pull_up=True)

        # Spindle index pin (active-HIGH, pull-down)
        self._spindle_pin = Button(cfg.GPIO_SPINDLE, pull_up=False)

        # ADC for potentiometer
        self._init_adc()

        # Enable motors by default, then give the ClearPath drives time to
        # come ready before any motion is commanded (matches the test).
        self._z_enable_pin.on()
        self._x_enable_pin.on()
        time.sleep(self._ENABLE_SETTLE_S)

        if self._debug:
            log.debug(
                "initialised: Z[step=%d dir=%d en=%d enc=%d/%d] "
                "X[step=%d dir=%d en=%d enc=%d/%d] spindle=%d adc=%s",
                cfg.GPIO_Z_STEP, cfg.GPIO_Z_DIR, cfg.GPIO_Z_ENABLE,
                cfg.GPIO_Z_ENC_A, cfg.GPIO_Z_ENC_B,
                cfg.GPIO_X_STEP, cfg.GPIO_X_DIR, cfg.GPIO_X_ENABLE,
                cfg.GPIO_X_ENC_A, cfg.GPIO_X_ENC_B,
                cfg.GPIO_SPINDLE,
                "ok" if self._ads_chan is not None else "none",
            )

    def _init_adc(self) -> None:
        backend = getattr(cfg, "ADC_BACKEND", "ads1015")
        if backend not in ("ads1015", "ads1115"):
            return
        try:
            import board
            import busio
            from adafruit_ads1x15.analog_in import AnalogIn
            from adafruit_ads1x15.ads1x15 import Pin
            i2c = busio.I2C(board.SCL, board.SDA)
            if backend == "ads1015":
                import adafruit_ads1x15.ads1015 as ADS
                self._ads = ADS.ADS1015(i2c)
            else:
                import adafruit_ads1x15.ads1115 as ADS
                self._ads = ADS.ADS1115(i2c)
            self._ads_chan = AnalogIn(self._ads, getattr(Pin, f"A{cfg.ADC_POT_CHANNEL}"))
            if self._debug:
                log.debug("%s ready on channel A%d", backend, cfg.ADC_POT_CHANNEL)
        except Exception as exc:
            print(f"[WARN] {backend} init failed: {exc} – pot reads will return midpoint")

    def shutdown(self) -> None:
        # Disable motors
        if self._z_enable_pin:
            self._z_enable_pin.off()
        if self._x_enable_pin:
            self._x_enable_pin.off()

        # Close all gpiozero devices to release GPIO pins
        if self._z_dec is not None:
            self._z_dec.close()
        if self._x_dec is not None:
            self._x_dec.close()
        if self._z_step_pin:
            self._z_step_pin.close()
        if self._z_dir_pin:
            self._z_dir_pin.close()
        if self._z_enable_pin:
            self._z_enable_pin.close()
        if self._x_step_pin:
            self._x_step_pin.close()
        if self._x_dir_pin:
            self._x_dir_pin.close()
        if self._x_enable_pin:
            self._x_enable_pin.close()

        for btn in self._btns.values():
            btn.close()
        if self._halfnut_btn:
            self._halfnut_btn.close()
        for lim_btn in self._limits.values():
            lim_btn.close()
        if self._spindle_pin:
            self._spindle_pin.close()

    # ── Encoders ────────────────────────────────────────────────────────────

    def get_z_encoder(self) -> int:
        steps = self._z_dec.steps if self._z_dec else 0
        if self._debug:
            if steps != self._z_enc_log:
                delta = 0 if self._z_enc_log is None else steps - self._z_enc_log
                self._z_enc_log = steps
                log.debug("Z encoder = %d (%+d)", steps, delta)
            else:
                now = time.monotonic()
                if now >= self._z_enc_hb_next:
                    self._z_enc_hb_next = now + self._enc_hb_interval_s
                    log.debug("Z encoder = %d (idle)", steps)
        return steps

    def set_z_encoder(self, value: int) -> None:
        if self._z_dec:
            self._z_dec.steps = value

    def get_x_encoder(self) -> int:
        steps = self._x_dec.steps if self._x_dec else 0
        if self._debug:
            if steps != self._x_enc_log:
                delta = 0 if self._x_enc_log is None else steps - self._x_enc_log
                self._x_enc_log = steps
                log.debug("X encoder = %d (%+d)", steps, delta)
            else:
                now = time.monotonic()
                if now >= self._x_enc_hb_next:
                    self._x_enc_hb_next = now + self._enc_hb_interval_s
                    log.debug("X encoder = %d (idle)", steps)
        return steps

    def set_x_encoder(self, value: int) -> None:
        if self._x_dec:
            self._x_dec.steps = value

    # ── Servos ──────────────────────────────────────────────────────────────

    def z_step(self, counts: int) -> None:
        self._send_steps(self._z_step_pin, self._z_dir_pin, counts)

    def x_step(self, counts: int) -> None:
        self._send_steps(self._x_step_pin, self._x_dir_pin, counts)

    def _send_steps(self, step_pin: OutputDevice | None, dir_pin: OutputDevice | None, counts: int) -> None:
        if counts == 0 or not step_pin or not dir_pin:
            return

        # Set direction, then let the drive latch it before the first STEP edge.
        if counts > 0:
            dir_pin.on()
        else:
            dir_pin.off()
        time.sleep(self._DIR_SETTLE_S)

        n = abs(counts)
        # Software-timed step pulses (matches the validated gearbox test).
        for _ in range(n):
            step_pin.on()
            time.sleep(self._STEP_PULSE_S)
            step_pin.off()
            time.sleep(self._STEP_GAP_S)

        if self._debug:
            axis = "Z" if step_pin is self._z_step_pin else "X"
            log.debug("%s step %+d (dir=%s)", axis, counts,
                      "FWD" if counts > 0 else "REV")

    def enable_z_motor(self, enabled: bool) -> None:
        if self._z_enable_pin:
            if enabled:
                self._z_enable_pin.on()
            else:
                self._z_enable_pin.off()

    def enable_x_motor(self, enabled: bool) -> None:
        if self._x_enable_pin:
            if enabled:
                self._x_enable_pin.on()
            else:
                self._x_enable_pin.off()

    # ── Spindle ─────────────────────────────────────────────────────────────

    def register_spindle_callback(self, cb: Callable[[], None]) -> None:
        if self._spindle_pin:
            # Button is active-HIGH, pull-downed.
            # when_pressed fires on rising edge to trigger on the index pulse.
            if self._debug:
                def _wrapped() -> None:
                    log.debug("spindle index pulse")
                    cb()
                self._spindle_pin.when_pressed = _wrapped
            else:
                self._spindle_pin.when_pressed = cb

    # ── Potentiometer ────────────────────────────────────────────────────────

    def read_potentiometer(self) -> int:
        if self._ads_chan is not None:
            # Map the pot voltage to the 0–1023 range calcFeed() expects, using
            # the configured reference.  Hold the last good value on a bus
            # glitch instead of lurching the feed rate (mirrors the test).
            try:
                voltage = self._ads_chan.voltage
                ref = getattr(cfg, "POT_REF_VOLTAGE", 3.3)
                scaled = int(voltage / ref * 1024)
                self._pot_last = max(0, min(1023, scaled))
                if self._debug and self._pot_last != self._pot_last_log:
                    self._pot_last_log = self._pot_last
                    log.debug("pot %.3fV -> %d/1023", voltage, self._pot_last)
            except OSError:
                pass  # keep the previous cached reading
            return self._pot_last
        return 512  # fallback midpoint

    # ── Digital inputs ──────────────────────────────────────────────────────

    def read_button(self, btn_id: int) -> bool:
        btn = self._btns.get(btn_id)
        if btn:
            # Since pull_up=True, is_pressed is True when the physical button links to ground (LOW)
            return btn.is_pressed
        return False

    def read_halfnut(self) -> bool:
        if self._halfnut_btn:
            # Since active HIGH & pull_up=False, is_pressed is True when physical pin is HIGH
            return self._halfnut_btn.is_pressed
        return False

    def read_limit_switch(self, axis: str, direction: str) -> bool:
        btn = self._limits.get((axis, direction))
        if btn:
            # Normally-closed switch: triggered when circuit opens (pin goes HIGH)
            # is_pressed=True means pin is LOW (normal, not triggered)
            # is_pressed=False means pin is HIGH (triggered)
            return not btn.is_pressed
        return False

    # ── Timing helpers ───────────────────────────────────────────────────────

    def micros(self) -> int:
        return (time.monotonic_ns() - self._start_time_ns) // 1000

    def delay_us(self, microseconds: int) -> None:
        if microseconds > 0:
            time.sleep(microseconds / 1_000_000)
