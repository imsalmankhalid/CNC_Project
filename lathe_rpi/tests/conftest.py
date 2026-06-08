"""
conftest.py – shared pytest fixtures for all test modules.

These fixtures provide a fresh MockInterface and reset MachineState
before every test to ensure complete isolation.
"""

import sys
import os

# Ensure the project root is on sys.path so tests can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from hal.mock_interface import MockInterface
from core.state_manager import reset_state


@pytest.fixture
def hw():
    """A freshly initialised MockInterface with a clean slate."""
    interface = MockInterface()
    interface.initialise()
    return interface


@pytest.fixture
def state():
    """A freshly reset MachineState singleton."""
    return reset_state()


@pytest.fixture
def hw_state(hw, state):
    """Convenience fixture returning (hw, state) together."""
    return hw, state
