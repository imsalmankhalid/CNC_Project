#!/bin/bash
# commit.sh – simple commit utility for the CNC project.
#
# Stages all changes (honouring .gitignore) and creates a commit.
#
# Usage:
#   ./commit.sh                      # commit with the default message
#   ./commit.sh "your message here"  # commit with a custom message
#
# It refuses to commit when there is nothing staged, and prints a short
# summary of what was committed.

set -euo pipefail

# Run from the repository root regardless of where the script is invoked from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

DEFAULT_MSG="Bench-test HAL: X axis working; Z working with limits disabled

- Sync Pi5 HAL to validated enc_drive_motor.py (pins, ADS1015, lgpio, timing)
- Fix X STEP/DIR pin swap in config.py (STEP=24, DIR=23)
- Add configurable console+file logging (log_setup.py) with debug flag
- Add LIMITS_ENABLED flag: a stuck Z+ limit was blocking all +Z motion;
  disable limits for bench testing so Z jogs both directions
- Remove cross-axis encoder freeze/restore so Z and X jog simultaneously
- UI: fix fullscreen button-bar overlap, add EXIT button + shortcuts
- Add desktop launcher (MbWLathe.desktop / install_desktop.sh) and testing guide"

MSG="${1:-$DEFAULT_MSG}"

echo "Repository: $REPO_ROOT"
echo "Staging all changes..."
git add -A

if git diff --cached --quiet; then
    echo "Nothing to commit – working tree clean."
    exit 0
fi

echo
echo "Files to be committed:"
git diff --cached --name-status
echo

git commit -m "$MSG"

echo
echo "Done. Latest commit:"
git --no-pager log -1 --stat
