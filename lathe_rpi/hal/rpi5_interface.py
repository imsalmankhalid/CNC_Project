"""
Raspberry Pi 5 Hardware Interface – uses gpiozero and native drivers for Pi 5 compatibility.

This back-end bypasses pigpio (which is incompatible with the RP1 on Pi 5)
and uses the modern python-gpiod/gpiozero libraries for GPIO and 
Adafruit Blinka for the I2C ADS1115 ADC.
"""

from __future__ import annotations

import time
from typing import Callable, Dict

import config as cfg
from .hardware_interface import HardwareInterface

try:
    from gpiozero import RotaryEncoder, Button, OutputDevice
    _GPIOZERO_AVAILABLE = True
except ImportError:
    _GPIOZERO_AVAILABLE = False


class Rpi5Interface(HardwareInterface):
    """Real hardware implementation for Raspberry Pi 5 using gpiozero."""

    _STEP_PULSE_S = 2e-6
    _STEP_GAP_S   = 2e-6

    def __init__(self) -> None:
        if not _GPIOZERO_AVAILABLE:
            raise RuntimeError(
                "gpiozero is not installed. Install it with: pip install gpiozero"
            )
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

        # ADS1115 handle (optional)
        self._ads = None
        self._ads_chan = None

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

        # Limit switches (active-LOW, internal pull-up)
        self._limits[("Z", "+")] = Button(cfg.GPIO_LIM_Z_PLUS, pull_up=True)
        self._limits[("Z", "-")] = Button(cfg.GPIO_LIM_Z_MINUS, pull_up=True)
        self._limits[("X", "+")] = Button(cfg.GPIO_LIM_X_PLUS, pull_up=True)
        self._limits[("X", "-")] = Button(cfg.GPIO_LIM_X_MINUS, pull_up=True)

        # Spindle index pin (active-HIGH, pull-down)
        self._spindle_pin = Button(cfg.GPIO_SPINDLE, pull_up=False)

        # ADC for potentiometer
        self._init_adc()

        # Enable motors by default
        self._z_enable_pin.on()
        self._x_enable_pin.on()

    def _init_adc(self) -> None:
        if cfg.ADC_BACKEND == "ads1115":
            try:
                import board
                import busio
                import adafruit_ads1x15.ads1115 as ADS
                from adafruit_ads1x15.analog_in import AnalogIn
                from adafruit_ads1x15.ads1x15 import Pin
                i2c = busio.I2C(board.SCL, board.SDA)
                self._ads = ADS.ADS1115(i2c)
                self._ads_chan = AnalogIn(self._ads, getattr(Pin, f"A{cfg.ADC_POT_CHANNEL}"))
            except Exception as exc:
                print(f"[WARN] ADS1115 init failed: {exc} – pot reads will return midpoint")

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
        return self._z_dec.steps if self._z_dec else 0

    def set_z_encoder(self, value: int) -> None:
        if self._z_dec:
            self._z_dec.steps = value

    def get_x_encoder(self) -> int:
        return self._x_dec.steps if self._x_dec else 0

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
        
        # Set direction
        if counts > 0:
            dir_pin.on()
        else:
            dir_pin.off()
            
        n = abs(counts)
        # Software-timed step pulses for Pi 5 fallback
        for _ in range(n):
            step_pin.on()
            time.sleep(self._STEP_PULSE_S)
            step_pin.off()
            time.sleep(self._STEP_GAP_S)

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
            self._spindle_pin.when_pressed = cb

    # ── Potentiometer ────────────────────────────────────────────────────────

    def read_potentiometer(self) -> int:
        if self._ads_chan is not None:
            # ADS1115 returns 0-26400 mV (gain=1); map to 0-1023
            try:
                raw_mv = self._ads_chan.voltage * 1000.0
                scaled = int(raw_mv / 3300.0 * 1024)
                return max(0, min(1023, scaled))
            except Exception:
                return 512
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
            # Active-LOW when triggered, so is_pressed means triggered because of pull_up=True
            return btn.is_pressed
        return False

    # ── Timing helpers ───────────────────────────────────────────────────────

    def micros(self) -> int:
        return (time.monotonic_ns() - self._start_time_ns) // 1000

    def delay_us(self, microseconds: int) -> None:
        if microseconds > 0:
            time.sleep(microseconds / 1_000_000)
