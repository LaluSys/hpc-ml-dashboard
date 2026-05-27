"""
Cross-platform launcher for HPC ML Dashboard.
- Linux/Mac: python launch.py
- Windows:   rename to launch.pyw for no console window, or double-click launch.pyw
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent

# Locate venv Python
if sys.platform == "win32":
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
else:
    venv_python = ROOT / ".venv" / "bin" / "python"

if not venv_python.exists():
    # Fallback: run setup first
    print("Venv nicht gefunden, führe setup aus...")
    setup = ROOT / ("setup.ps1" if sys.platform == "win32" else "setup.sh")
    subprocess.run(["powershell", str(setup)] if sys.platform == "win32" else ["bash", str(setup)])

kwargs = {}
if sys.platform == "win32":
    # Hide the console window on Windows
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    kwargs["startupinfo"] = si

proc = subprocess.Popen(
    [
        str(venv_python), "-m", "streamlit", "run",
        str(ROOT / "dashboard.py"),
        "--server.headless=true",
        "--server.port=8501",
    ],
    cwd=ROOT,
    **kwargs,
)

# Wait for server to be ready, then open browser
time.sleep(2)
webbrowser.open("http://localhost:8501")

# Keep process alive until window is closed
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
