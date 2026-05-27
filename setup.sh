#!/bin/bash
set -e
echo "=== HPC ML Dashboard Setup ==="

if ! command -v python3 &>/dev/null; then
    echo "FEHLER: Python 3 nicht gefunden. Bitte Python >= 3.10 installieren."
    exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    echo ""
    echo "config.yaml wurde erstellt."
    echo "WICHTIG: Öffne config.yaml und trage deine uk-Nummer ein!"
fi

echo ""
echo "Setup abgeschlossen."
echo "Starten:"
echo "  source .venv/bin/activate"
echo "  streamlit run dashboard.py"
