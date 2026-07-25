#!/bin/bash
# MbW Lathe System – Launcher Script
# Activates the virtual environment and starts the main application.

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/env/bin/activate"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run the main application
exec python main.py "$@"
