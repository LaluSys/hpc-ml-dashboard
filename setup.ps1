# HPC ML Dashboard Setup (Windows)
Write-Host "=== HPC ML Dashboard Setup ===" -ForegroundColor Cyan

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if (-not (Test-Path "config.yaml")) {
    Copy-Item "config.example.yaml" "config.yaml"
    Write-Host ""
    Write-Host "config.yaml wurde erstellt." -ForegroundColor Yellow
    Write-Host "WICHTIG: Oeffne config.yaml und trage deine uk-Nummer ein!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup abgeschlossen." -ForegroundColor Green
Write-Host "Starten:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  streamlit run dashboard.py"
