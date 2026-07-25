"""
MbW Lathe – Raspberry Pi Edition
Entry Point
"""

import sys
import os

# Ensure the project root is always on the Python path,
# regardless of the working directory from which main.py is launched.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Allow '--windowed' flag to force non-fullscreen mode during desktop testing
if "--windowed" in sys.argv:
    import config as _cfg
    _cfg.FULLSCREEN = False
    sys.argv.remove("--windowed")

# Configure logging (console + rotating file) before anything else runs.
from log_setup import setup_logging
setup_logging()

from ui.app import run_app

if __name__ == "__main__":
    run_app()
