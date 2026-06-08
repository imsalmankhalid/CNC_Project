"""
Base Mode
=========
Abstract base class for all lathe operating modes.  Each mode owns its
state machine and communicates with the UI through MachineState and Qt signals.
"""

from __future__ import annotations
import abc
from typing import TYPE_CHECKING

from core.state_manager import get_state

if TYPE_CHECKING:
    from hal.hardware_interface import HardwareInterface


class BaseMode(abc.ABC):
    """Abstract lathe mode."""

    def __init__(self, hw: "HardwareInterface") -> None:
        self._hw = hw
        self._state = get_state()
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    @abc.abstractmethod
    def enter(self) -> None:
        """Called when the mode becomes active."""

    @abc.abstractmethod
    def exit(self) -> None:
        """Called when the mode is deactivated."""

    @abc.abstractmethod
    def tick(self) -> None:
        """
        Called by the main loop at a moderate rate (~20 Hz).
        Used for state-machine progression in wizard-style modes.
        """
