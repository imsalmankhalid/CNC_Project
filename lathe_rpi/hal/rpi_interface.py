"""
Raspberry Pi Hardware Interface – uses pigpio for hardware-timed GPIO.

Requirements
------------
* pigpio daemon must be running:  sudo systemctl enable pigpiod && sudo systemctl start pigpiod
* Run the main application with sufficient privileges for scheduling:
      sudo nice -n -20 python main.py
  or, better, configure /etc/security/limits.conf for SCHED_FIFO.

pigpio provides:
  * Hardware-interrupt callbacks for encoder quadrature decoding
  * Hardware-timed wave-based step pulse generation (~1 µs accuracy)
  * GPIO read/write for direction, enable, buttons, limit switches
"""

from __future__ import annotations

import time
from typing import Callable

import config as cfg
from .hardware_interface import HardwareInterface

try:
    import pigpio  # type: ignore
    _PIGPIO_AVAILABLE = True
except ImportError:
    _PIGPIO_AVAILABLE = False


class QuadratureDecoder:
    """Lightweight quadrature decoder driven by pigpio edge callbacks."""

    _STATE_TABLE = {
        (0, 0, 0, 1): +1, (0, 0, 1, 0): -1,
        (0, 1, 0, 0): -1, (0, 1, 1, 1): +1,
        (1, 0, 0, 0): +1, (1, 0, 1, 1): -1,
        (1, 1, 0, 1): -1, (1, 1, 1, 0): +1,
    }

    def __init__(self, pi: "pigpio.pi", pin_a: int, pin_b: int) -> None:
        self._pi = pi
        self._pin_a = pin_a
        self._pin_b = pin_b
        self._count: int = 0
        self._last_a: int = 0
        self._last_b: int = 0

    def start(self) -> None:
        self._pi.set_mode(self._pin_a, pigpio.INPUT)
        self._pi.set_mode(self._pin_b, pigpio.INPUT)
        self._pi.set_pull_up_down(self._pin_a, pigpio.PUD_UP)
        self._pi.set_pull_up_down(self._pin_b, pigpio.PUD_UP)
        self._last_a = self._pi.read(self._pin_a)
        self._last_b = self._pi.read(self._pin_b)
        self._pi.callback(self._pin_a, pigpio.EITHER_EDGE, self._edge)
        self._pi.callback(self._pin_b, pigpio.EITHER_EDGE, self._edge)

    def _edge(self, gpio: int, level: int, _tick: int) -> None:
        new_a = level if gpio == self._pin_a else self._pi.read(self._pin_a)
        new_b = level if gpio == self._pin_b else self._pi.read(self._pin_b)
        delta = self._STATE_TABLE.get(
            (self._last_a, self._last_b, new_a, new_b), 0
        )
        self._count += delta
        self._last_a = new_a
        self._last_b = new_b

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        self._count = value


class RpiInterface(HardwareInterface):
    """Real hardware implementation using pigpio."""

    # Minimum step pulse width (µs) for ClearPath SDSK servos
    _STEP_PULSE_US = 2
    # Minimum inter-pulse gap (µs)
    _STEP_GAP_US   = 2

    def __init__(self) -> None:
        if not _PIGPIO_AVAILABLE:
            raise RuntimeError(
                "pigpio is not installed.  Install it with: pip install pigpio"
            )
        self._pi: pigpio.pi | None = None
        self._z_dec: QuadratureDecoder | None = None
        self._x_dec: QuadratureDecoder | None = None
        self._start_time_ns: int = 0
        self._spindle_cb_fn: Callable[[], None] | None = None
        self._spindle_cb_handle = None

        # ADS1115 handle (optional)
        self._ads = None
        self._ads_chan = None

    # ── Life-cycle ──────────────────────────────────────────────────────────

    def initialise(self) -> None:
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError(
                "Cannot connect to pigpiod.  "
                "Run: sudo systemctl start pigpiod"
            )
        self._start_time_ns = time.monotonic_ns()

        # Encoders
        self._z_dec = QuadratureDecoder(self._pi, cfg.GPIO_Z_ENC_A, cfg.GPIO_Z_ENC_B)
        self._x_dec = QuadratureDecoder(self._pi, cfg.GPIO_X_ENC_A, cfg.GPIO_X_ENC_B)
        self._z_dec.start()
        self._x_dec.start()

        # Servo outputs
        for pin in (cfg.GPIO_Z_STEP, cfg.GPIO_Z_DIR, cfg.GPIO_Z_ENABLE,
                    cfg.GPIO_X_STEP, cfg.GPIO_X_DIR, cfg.GPIO_X_ENABLE):
            self._pi.set_mode(pin, pigpio.OUTPUT)
            self._pi.write(pin, 0)

        # Buttons (active-LOW)
        for pin in (cfg.GPIO_BTN_1, cfg.GPIO_BTN_2, cfg.GPIO_BTN_3):
            self._pi.set_mode(pin, pigpio.INPUT)
            self._pi.set_pull_up_down(pin, pigpio.PUD_UP)

        # Half-nut switch (active-HIGH)
        self._pi.set_mode(cfg.GPIO_HALFNUT, pigpio.INPUT)
        self._pi.set_pull_up_down(cfg.GPIO_HALFNUT, pigpio.PUD_DOWN)

        # Limit switches (active-LOW, NO contact)
        for pin in (cfg.GPIO_LIM_Z_PLUS, cfg.GPIO_LIM_Z_MINUS,
                    cfg.GPIO_LIM_X_PLUS, cfg.GPIO_LIM_X_MINUS):
            self._pi.set_mode(pin, pigpio.INPUT)
            self._pi.set_pull_up_down(pin, pigpio.PUD_UP)

        # Spindle index (active-HIGH pulse)
        self._pi.set_mode(cfg.GPIO_SPINDLE, pigpio.INPUT)
        self._pi.set_pull_up_down(cfg.GPIO_SPINDLE, pigpio.PUD_DOWN)

        # ADC for potentiometer
        self._init_adc()

        # Motors enabled by default
        self._pi.write(cfg.GPIO_Z_ENABLE, 1)
        self._pi.write(cfg.GPIO_X_ENABLE, 1)

    def _init_adc(self) -> None:
        backend = getattr(cfg, "ADC_BACKEND", "ads1015")
        if backend in ("ads1015", "ads1115"):
            try:
                import board          # type: ignore
                import busio          # type: ignore
                from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore
                from adafruit_ads1x15.ads1x15 import Pin  # type: ignore
                i2c = busio.I2C(board.SCL, board.SDA)
                if backend == "ads1015":
                    import adafruit_ads1x15.ads1015 as ADS  # type: ignore
                    self._ads = ADS.ADS1015(i2c)
                else:
                    import adafruit_ads1x15.ads1115 as ADS  # type: ignore
                    self._ads = ADS.ADS1115(i2c)
                self._ads_chan = AnalogIn(self._ads, getattr(Pin, f"A{cfg.ADC_POT_CHANNEL}"))
            except Exception as exc:
                print(f"[WARN] {backend} init failed: {exc} – pot reads will return midpoint")

    def shutdown(self) -> None:
        if self._pi:
            for pin in (cfg.GPIO_Z_ENABLE, cfg.GPIO_X_ENABLE):
                self._pi.write(pin, 0)
            self._pi.stop()
            self._pi = None

    # ── Encoders ────────────────────────────────────────────────────────────

    def get_z_encoder(self) -> int:
        return self._z_dec.count  # type: ignore[union-attr]

    def set_z_encoder(self, value: int) -> None:
        self._z_dec.count = value  # type: ignore[union-attr]

    def get_x_encoder(self) -> int:
        return self._x_dec.count  # type: ignore[union-attr]

    def set_x_encoder(self, value: int) -> None:
        self._x_dec.count = value  # type: ignore[union-attr]

    # ── Servos ──────────────────────────────────────────────────────────────

    def z_step(self, counts: int) -> None:
        self._send_steps(cfg.GPIO_Z_STEP, cfg.GPIO_Z_DIR, counts)

    def x_step(self, counts: int) -> None:
        self._send_steps(cfg.GPIO_X_STEP, cfg.GPIO_X_DIR, counts)

    def _send_steps(self, step_pin: int, dir_pin: int, counts: int) -> None:
        """Generate hardware-timed step pulses via pigpio waveforms."""
        if counts == 0 or not self._pi:
            return
        direction = 1 if counts > 0 else 0
        self._pi.write(dir_pin, direction)
        n = abs(counts)
        # Build a minimal waveform: n step pulses
        pulses = []
        for _ in range(n):
            pulses.append(pigpio.pulse(1 << step_pin, 0, self._STEP_PULSE_US))
            pulses.append(pigpio.pulse(0, 1 << step_pin, self._STEP_GAP_US))
        self._pi.wave_clear()
        self._pi.wave_add_generic(pulses)
        wid = self._pi.wave_create()
        if wid >= 0:
            self._pi.wave_send_once(wid)
            while self._pi.wave_tx_busy():
                pass
            self._pi.wave_delete(wid)

    def enable_z_motor(self, enabled: bool) -> None:
        if self._pi:
            self._pi.write(cfg.GPIO_Z_ENABLE, 1 if enabled else 0)

    def enable_x_motor(self, enabled: bool) -> None:
        if self._pi:
            self._pi.write(cfg.GPIO_X_ENABLE, 1 if enabled else 0)

    # ── Spindle ─────────────────────────────────────────────────────────────

    def register_spindle_callback(self, cb: Callable[[], None]) -> None:
        self._spindle_cb_fn = cb
        if self._pi:
            self._spindle_cb_handle = self._pi.callback(
                cfg.GPIO_SPINDLE, pigpio.RISING_EDGE, lambda *_: cb()
            )

    # ── Potentiometer ────────────────────────────────────────────────────────

    def read_potentiometer(self) -> int:
        if self._ads_chan is not None:
            # Map the pot voltage to the 0–1023 range calcFeed() expects.
            ref = getattr(cfg, "POT_REF_VOLTAGE", 3.3)
            scaled = int(self._ads_chan.voltage / ref * 1024)
            return max(0, min(1023, scaled))
        return 512  # fallback midpoint

    # ── Digital inputs ──────────────────────────────────────────────────────

    _BTN_PINS = {1: cfg.GPIO_BTN_1, 2: cfg.GPIO_BTN_2, 3: cfg.GPIO_BTN_3}

    def read_button(self, btn_id: int) -> bool:
        pin = self._BTN_PINS.get(btn_id)
        if pin and self._pi:
            return self._pi.read(pin) == 0  # active-LOW
        return False

    def read_halfnut(self) -> bool:
        if self._pi:
            return self._pi.read(cfg.GPIO_HALFNUT) == 1
        return False

    _LIMIT_PINS = {
        ("Z", "+"): cfg.GPIO_LIM_Z_PLUS,
        ("Z", "-"): cfg.GPIO_LIM_Z_MINUS,
        ("X", "+"): cfg.GPIO_LIM_X_PLUS,
        ("X", "-"): cfg.GPIO_LIM_X_MINUS,
    }

    def read_limit_switch(self, axis: str, direction: str) -> bool:
        pin = self._LIMIT_PINS.get((axis, direction))
        if pin and self._pi:
            return self._pi.read(pin) == 0  # active-LOW = triggered
        return False

    # ── Timing helpers ───────────────────────────────────────────────────────

    def micros(self) -> int:
        return (time.monotonic_ns() - self._start_time_ns) // 1000

    def delay_us(self, microseconds: int) -> None:
        if microseconds > 0:
            time.sleep(microseconds / 1_000_000)
