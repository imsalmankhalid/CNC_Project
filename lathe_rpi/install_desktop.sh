#!/bin/bash
# Installs the "MbW Lathe" desktop launcher so the app can be started with a
# double-click from the Desktop and from the applications menu.
#
# Usage:
#   ./install_desktop.sh            # normal launcher
#   ./install_desktop.sh --debug    # launcher that also enables debug logging
#
# Re-run this any time the project is moved to refresh the paths.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_CMD="$SCRIPT_DIR/run_lathe.sh"
NAME="MbW Lathe"

# Append --debug to the launched command if requested.
if [[ " $* " == *" --debug "* ]]; then
    RUN_CMD="$RUN_CMD --debug"
    NAME="MbW Lathe (debug)"
fi

DESKTOP_CONTENT="[Desktop Entry]
Version=1.0
Type=Application
Name=$NAME
GenericName=CNC Lathe Control
Comment=Start the MbW Lathe control system
Exec=$RUN_CMD
Path=$SCRIPT_DIR
Icon=applications-engineering
Terminal=false
Categories=Utility;Engineering;
StartupNotify=true"

# Make sure the launcher script itself is executable.
chmod +x "$SCRIPT_DIR/run_lathe.sh"

install_to() {
    local dest_dir="$1"
    [ -d "$dest_dir" ] || mkdir -p "$dest_dir"
    local dest_file="$dest_dir/MbWLathe.desktop"
    echo "$DESKTOP_CONTENT" > "$dest_file"
    chmod +x "$dest_file"
    # Mark the launcher as trusted so the file manager does not warn on launch.
    if command -v gio >/dev/null 2>&1; then
        gio set "$dest_file" metadata::trusted true 2>/dev/null || true
    fi
    echo "  installed: $dest_file"
}

echo "Installing '$NAME' launcher..."
install_to "$HOME/.local/share/applications"

if [ -d "$HOME/Desktop" ]; then
    install_to "$HOME/Desktop"
else
    echo "  (no ~/Desktop folder found – skipped Desktop icon)"
fi

# Refresh the desktop database if the tool is available.
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo "Done. Look for '$NAME' on the Desktop and in the applications menu."
