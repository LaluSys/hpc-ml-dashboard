#!/bin/bash
# Legt einen Desktop-Shortcut für HPC ML Dashboard an.
# Nutzung: bash install_shortcut.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP="$HOME/Desktop"
DESKTOP_FILE="$DESKTOP/hpc-ml-dashboard.desktop"

# XDG Desktop fallback
[ -d "$DESKTOP" ] || DESKTOP="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
mkdir -p "$DESKTOP"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=HPC ML Dashboard
Comment=KI-Training auf dem Uni-Kassel Cluster
Exec=python3 $SCRIPT_DIR/launch.py
Path=$SCRIPT_DIR
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Science;Education;
EOF

chmod +x "$DESKTOP_FILE"

# Some desktops require marking as trusted
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true

echo "✓ Shortcut erstellt: $DESKTOP_FILE"
echo "  Doppelklick auf dem Desktop startet das Dashboard."
