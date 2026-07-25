#!/bin/bash
# MbW Lathe System – Launcher Script
# Activates the virtual environment and starts the main application.

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/env/bin/activate"

# Change to the project directory
cd "$SCRIPT_DIR"

# Enable HAL/motion debug logging (encoders, pot, steps) when --debug is passed.
if [[ " $* " == *" --debug "* ]]; then
    export LATHE_DEBUG_HAL=1
    # Drop --debug so it is not forwarded to main.py
    set -- "${@/--debug/}"
    echo "[run_lathe] debug logging enabled (LATHE_DEBUG_HAL=1)"
fi

# Run the main application
exec python main.py "$@"
