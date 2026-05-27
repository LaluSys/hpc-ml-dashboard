# HPC ML Dashboard Setup (Windows)
# Fenster bleibt offen bis Enter gedrueckt wird

try {
    Write-Host "=== HPC ML Dashboard Setup ===" -ForegroundColor Cyan
    Write-Host ""

    # --- Python suchen ---
    $PythonExe = $null
    foreach ($candidate in @("py", "python", "python3")) {
        try {
            $ver = & $candidate --version 2>&1
            if ($ver -match "Python 3\.(\d+)") {
                $minor = [int]$Matches[1]
                if ($minor -ge 10) {
                    $PythonExe = $candidate
                    Write-Host "Python gefunden: $ver ($candidate)" -ForegroundColor Green
                    break
                } else {
                    Write-Host "Python $ver zu alt (mind. 3.10 noetig)..." -ForegroundColor Yellow
                }
            }
        } catch { }
    }

    if (-not $PythonExe) {
        Write-Host ""
        Write-Host "FEHLER: Python 3.10+ nicht gefunden." -ForegroundColor Red
        Write-Host ""
        Write-Host "Bitte Python installieren:" -ForegroundColor Yellow
        Write-Host "  1. https://www.python.org/downloads/ oeffnen"
        Write-Host "  2. 'Download Python 3.x' klicken"
        Write-Host "  3. Installer starten und 'Add Python to PATH' aktivieren"
        Write-Host "  4. PowerShell neu starten, dann setup.ps1 erneut ausfuehren"
        Write-Host ""
        Read-Host "Enter druecken zum Beenden"
        exit 1
    }

    # --- Venv erstellen ---
    Write-Host "Erstelle virtuelle Umgebung..." -ForegroundColor Cyan
    & $PythonExe -m venv .venv
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        throw "venv konnte nicht erstellt werden."
    }

    $VenvPython = ".\.venv\Scripts\python.exe"

    # --- pip sicherstellen ---
    Write-Host "Aktualisiere pip..." -ForegroundColor Cyan
    & $VenvPython -m ensurepip --upgrade 2>&1 | Out-Null
    & $VenvPython -m pip install --quiet --upgrade pip

    # --- Abhaengigkeiten installieren ---
    Write-Host "Installiere Abhaengigkeiten (kann 1-2 Minuten dauern)..." -ForegroundColor Cyan
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Fehler beim Installieren der Pakete."
    }

    # --- Config ---
    if (-not (Test-Path "config.yaml")) {
        Copy-Item "config.example.yaml" "config.yaml"
    }

    # --- Shortcut anbieten ---
    Write-Host ""
    Write-Host "Setup abgeschlossen!" -ForegroundColor Green
    Write-Host ""
    $ans = Read-Host "Desktop-Shortcut erstellen? (j/n)"
    if ($ans -eq "j" -or $ans -eq "J") {
        & powershell -ExecutionPolicy Bypass -File .\install_shortcut.ps1
    }

    Write-Host ""
    Write-Host "Fertig! Dashboard starten:" -ForegroundColor Cyan
    Write-Host "  Doppelklick auf den Desktop-Shortcut" -ForegroundColor White
    Write-Host "  oder: python launch.pyw" -ForegroundColor White

} catch {
    Write-Host ""
    Write-Host "FEHLER: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Enter druecken zum Beenden"
