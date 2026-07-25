#!/usr/bin/env bash
# Wrapper to activate project venv and run combined_tests.py
PROJECT_DIR="/home/cnc/CNC_Project/lathe_rpi"

cd "$PROJECT_DIR" || { echo "Failed to cd to $PROJECT_DIR"; exit 1; }

# Activate virtualenv if available
if [ -f "$PROJECT_DIR/env/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$PROJECT_DIR/env/bin/activate"
fi

# Choose python: prefer venv python when activated
if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
  PY="$VIRTUAL_ENV/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi

echo "Using python: $PY"

# Run the combined tests script
"$PY" "${PROJECT_DIR}/test/combined_tests.py"

echo
read -p "Tests finished. Press Enter to close this terminal..." -r
