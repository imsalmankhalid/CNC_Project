"""
Global Machine State
====================
A single shared dataclass that all modes and the UI read / write.
Avoid adding business logic here – this is pure state storage.
Thread-safety: individual field assignments are GIL-protected in CPython;
for multi-field atomic updates use the provided context manager.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import List


@dataclass
class MachineState:
    # ── Position tracking (motor counts, signed) ─────────────────────────
    mtr_pos_z: int = 0          # absolute Z motor count from power-on
    mtr_pos_x: int = 0          # absolute X motor count from power-on

    # ── Position memory slots (3 per axis) ───────────────────────────────
    mem_offset_z: List[int] = field(default_factory=lambda: [0, 0, 0])
    mem_offset_x: List[int] = field(default_factory=lambda: [0, 0, 0])
    active_mem_z: int = 0       # currently displayed memory slot (0/1/2)
    active_mem_x: int = 0

    # ── Z auto-stop (3 values per memory slot; 999_999 = not set) ────────
    mem_stop_z: List[int] = field(default_factory=lambda: [999_999, 999_999, 999_999])

    # ── Units ─────────────────────────────────────────────────────────────
    unit_mm: bool = True        # True=mm display, False=inch display

    # ── Spindle ───────────────────────────────────────────────────────────
    spindle_rpm: float = 0.0
    spindle_index_time_us: int = 0   # last index pulse timestamp (µs)
    spindle_prev_index_us: int = 0

    # ── Feed rate ─────────────────────────────────────────────────────────
    feed_rate_mm: float = 12.7  # mm/min (set by potentiometer)
    feed_rate_ipm: float = 0.5  # IPM (display value)

    # ── Mode ──────────────────────────────────────────────────────────────
    # 0=standard DRO  1=thread  2=(reserved)  3=profile  4=radius  999=menu
    mode: int = 0

    # ── Limit switch status ───────────────────────────────────────────────
    limit_z_plus:  bool = False
    limit_z_minus: bool = False
    limit_x_plus:  bool = False
    limit_x_minus: bool = False

    # Per-axis "limit hit" (either direction).  A single switch per axis feeds
    # these; motion on that axis is blocked while True and the UI alarms.
    limit_z: bool = False
    limit_x: bool = False

    # ── Emergency stop ────────────────────────────────────────────────────
    estop: bool = False

    # ── Internal lock for multi-field atomic updates ──────────────────────
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def atomic(self):
        """Context manager for multi-field atomic updates."""
        return self._lock

    # ── Convenience helpers ───────────────────────────────────────────────

    def z_display_mm(self) -> float:
        """Z position in mm relative to active memory zero."""
        from config import Z_PITCH, Z_MTR_CNT_PER_REV
        counts_from_zero = self.mtr_pos_z - self.mem_offset_z[self.active_mem_z]
        return counts_from_zero * (Z_PITCH / Z_MTR_CNT_PER_REV)

    def x_display_mm(self) -> float:
        """X position in mm relative to active memory zero."""
        from config import X_PITCH, X_MTR_CNT_PER_REV
        counts_from_zero = self.mtr_pos_x - self.mem_offset_x[self.active_mem_x]
        return counts_from_zero * (X_PITCH / X_MTR_CNT_PER_REV)

    def z_display(self) -> float:
        """Z display value in current units."""
        mm = self.z_display_mm()
        return mm if self.unit_mm else mm / 25.4

    def x_display(self) -> float:
        """X display value in current units."""
        mm = self.x_display_mm()
        return mm if self.unit_mm else mm / 25.4

    def unit_label(self) -> str:
        return "mm" if self.unit_mm else "in"


# ── Singleton ─────────────────────────────────────────────────────────────────
_state: MachineState | None = None


def get_state() -> MachineState:
    global _state
    if _state is None:
        _state = MachineState()
    return _state


def reset_state() -> MachineState:
    """Create a fresh state – used in tests to ensure isolation."""
    global _state
    _state = MachineState()
    return _state
