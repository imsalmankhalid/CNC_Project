
"""
MbW Lathe HMI  –  Live Demo  (no hardware required)
====================================================
Launches the full-screen HMI with a MockInterface and drives it with
QTimers to produce continuously changing display values:

    • Z handwheel simulation  → Z DRO digits animate
    • X handwheel simulation  → X DRO digits animate
    • Spindle at ~1 200 RPM   → RPM display animates
    • Potentiometer sweep     → Feed-rate (IPM) display animates
    • Scenario steps every 8 s → demonstrates Z-stop, unit toggle,
                                  memory slots, limit triggers

Run from the lathe_rpi/ directory:

    python demo.py

By default opens in windowed (800×480) mode so you can watch
the display on the desktop.  To force fullscreen on an RPi,
remove the FULLSCREEN override below.
"""

from __future__ import annotations

import os
import sys

# ── Path bootstrap ────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Force windowed mode for desktop demo ─────────────────────────────────────
import config as cfg
cfg.FULLSCREEN = False

# ── Qt imports (must come after path bootstrap) ───────────────────────────────
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from hal.mock_interface import MockInterface
from core.state_manager import reset_state
from ui.app import MainWindow


# ─────────────────────────────────────────────────────────────────────────────
#  Demo configuration
# ─────────────────────────────────────────────────────────────────────────────

# Z encoder: counts injected per tick and tick interval
_Z_TICK_COUNTS  = 20       # counts per timer tick
_Z_TICK_MS      = 25       # ms between ticks  (20 cnt / 25 ms = 800 cnt/s)
_Z_REVERSE_MS   = 4_000    # reverse Z direction every N ms

# X encoder: counts injected per tick and tick interval
_X_TICK_COUNTS  = 8        # counts per timer tick
_X_TICK_MS      = 35       # ms between ticks
_X_REVERSE_MS   = 6_500    # reverse X direction every N ms

# Spindle: pulse interval in ms
# 1 pulse / revolution  →  50 ms = 1 200 RPM
_SPINDLE_TICK_MS = 50

# Pot sweep: delta applied per tick and tick interval
_POT_TICK_DELTA  = 30
_POT_TICK_MS     = 150

# Scenario step interval
_SCENARIO_MS     = 8_000


# ─────────────────────────────────────────────────────────────────────────────
#  Demo class
# ─────────────────────────────────────────────────────────────────────────────

class LatheDemo:
    """
    Owns all QTimers that inject mock inputs.
    Must be created *after* QApplication exists.
    """

    def __init__(self, hw: MockInterface, window: MainWindow) -> None:
        self._hw     = hw
        self._window = window
        self._state  = window._state

        # Direction trackers (±1)
        self._z_dir = 1
        self._x_dir = 1
        self._pot   = 512
        self._pot_dir = 1

        # Scenario index
        self._scenario = 0
        self._scenarios = [
            self._scene_normal,
            self._scene_z_stop,
            self._scene_unit_toggle,
            self._scene_memory_cycle,
            self._scene_limit_trigger,
            self._scene_clear_limit,
            self._scene_return_normal,
        ]

        # ── Create timers ─────────────────────────────────────────────────────
        self._tmr_z        = self._make_timer(_Z_TICK_MS,       self._tick_z)
        self._tmr_x        = self._make_timer(_X_TICK_MS,       self._tick_x)
        self._tmr_z_rev    = self._make_timer(_Z_REVERSE_MS,    self._reverse_z)
        self._tmr_x_rev    = self._make_timer(_X_REVERSE_MS,    self._reverse_x)
        self._tmr_spindle  = self._make_timer(_SPINDLE_TICK_MS, self._tick_spindle)
        self._tmr_pot      = self._make_timer(_POT_TICK_MS,     self._tick_pot)
        self._tmr_scenario = self._make_timer(_SCENARIO_MS,     self._next_scenario)

        # Print a header
        print()
        print("═" * 60)
        print("  MbW Lathe HMI  –  Live Demo")
        print("  Mock hardware only – no physical controller needed")
        print("═" * 60)
        print()
        print("  Z-axis:  sweeping back & forth every 4 s")
        print("  X-axis:  sweeping back & forth every 6.5 s")
        print("  Spindle: simulated at ~1 200 RPM")
        print("  Feed:    potentiometer sweep (IPM display animates)")
        print(f"  Scenario steps every {_SCENARIO_MS // 1000} s  (see console)")
        print()
        print("  Close the window (or Ctrl-C) to exit.")
        print("─" * 60)

    # ── Timer factory ─────────────────────────────────────────────────────────

    @staticmethod
    def _make_timer(interval_ms: int, slot) -> QTimer:
        t = QTimer()
        t.setInterval(interval_ms)
        t.timeout.connect(slot)
        t.start()
        return t

    # ── Encoder ticks ─────────────────────────────────────────────────────────

    def _tick_z(self) -> None:
        self._hw.simulate_z_encoder(self._z_dir * _Z_TICK_COUNTS)

    def _tick_x(self) -> None:
        self._hw.simulate_x_encoder(self._x_dir * _X_TICK_COUNTS)

    def _reverse_z(self) -> None:
        self._z_dir *= -1
        direction = "→ +Z" if self._z_dir > 0 else "← −Z"
        z_mm = self._state.z_display_mm()
        print(f"[DEMO] Z reverses {direction}  (was {z_mm:+.3f} mm)")

    def _reverse_x(self) -> None:
        self._x_dir *= -1
        direction = "→ +X" if self._x_dir > 0 else "← −X"
        x_mm = self._state.x_display_mm()
        print(f"[DEMO] X reverses {direction}  (was {x_mm:+.3f} mm)")

    # ── Spindle tick ──────────────────────────────────────────────────────────

    def _tick_spindle(self) -> None:
        self._hw.fire_spindle_pulse()

    # ── Pot sweep ─────────────────────────────────────────────────────────────

    def _tick_pot(self) -> None:
        self._pot += self._pot_dir * _POT_TICK_DELTA
        if self._pot >= 1023:
            self._pot = 1023
            self._pot_dir = -1
        elif self._pot <= 0:
            self._pot = 0
            self._pot_dir = 1
        self._hw.set_pot_value(self._pot)

    # ── Scenario steps ────────────────────────────────────────────────────────

    def _next_scenario(self) -> None:
        fn = self._scenarios[self._scenario % len(self._scenarios)]
        fn()
        self._scenario += 1

    def _scene_normal(self) -> None:
        print("\n[DEMO] ─── Scene: Normal DRO operation ───")
        print("         Z and X handwheels simulated, spindle ~1200 RPM")

    def _scene_z_stop(self) -> None:
        """Set a Z auto-stop at the current Z position."""
        st = self._state
        st.mem_stop_z[st.active_mem_z] = st.mtr_pos_z
        z_mm = st.z_display_mm()
        print(f"\n[DEMO] ─── Scene: Z auto-stop SET at {z_mm:+.3f} mm ───")
        print("         Z-STOP panel should now show position value")

    def _scene_unit_toggle(self) -> None:
        """Switch from mm to inch."""
        self._state.unit_mm = not self._state.unit_mm
        unit = "mm" if self._state.unit_mm else "in"
        print(f"\n[DEMO] ─── Scene: Unit toggle → {unit} ───")
        print(f"         DRO labels should now read in {'millimetres' if self._state.unit_mm else 'inches'}")

    def _scene_memory_cycle(self) -> None:
        """Cycle to the next memory slot."""
        st = self._state
        old = st.active_mem_z
        st.active_mem_z = (st.active_mem_z + 1) % 3
        print(f"\n[DEMO] ─── Scene: Z memory M{old + 1} → M{st.active_mem_z + 1} ───")
        print("         Badge label on DRO should change to new slot")

    def _scene_limit_trigger(self) -> None:
        """Simulate a Z+ limit switch hit."""
        self._hw.trigger_limit("Z", "+", True)
        print("\n[DEMO] ─── Scene: Z+ limit triggered ───")
        print("         Z+ indicator in LIMITS panel should go red ⬛")

    def _scene_clear_limit(self) -> None:
        """Clear the limit and zero out the position."""
        self._hw.trigger_limit("Z", "+", False)
        st = self._state
        # Reset zero reference for the current memory slot
        st.mem_offset_z[st.active_mem_z] = st.mtr_pos_z
        print("\n[DEMO] ─── Scene: Z+ limit cleared + Z zeroed ───")
        print("         Z+ indicator back to ◉,  Z DRO resets to +0.000")

    def _scene_return_normal(self) -> None:
        """Restore mm units if we're in inch."""
        if not self._state.unit_mm:
            self._state.unit_mm = True
            print("\n[DEMO] ─── Scene: Units restored to mm ───")
        else:
            print("\n[DEMO] ─── Scene: Looping back to top ───")
        # Reset scenario counter
        self._scenario = 0


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # Fresh machine state so everything starts at zero
    reset_state()

    # Pre-create the mock interface so we can keep a reference for injection
    hw = MockInterface()
    hw.initialise()

    # Start Qt
    app = QApplication(sys.argv)
    app.setApplicationName("MbW Lathe Demo")

    # Build the window with injected hardware
    window = MainWindow(hw=hw)
    window.setWindowTitle("MbW Lathe HMI  –  Live Demo  (Mock Hardware)")
    window.show()

    # Start demo injection timers (must be created after QApplication)
    _demo = LatheDemo(hw, window)  # noqa: F841  (kept alive by reference)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
