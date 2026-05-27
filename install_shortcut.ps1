# Legt einen Desktop-Shortcut für HPC ML Dashboard an (Windows).
# Nutzung: .\install_shortcut.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LaunchPyw = Join-Path $ScriptDir "launch.pyw"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "HPC ML Dashboard.lnk"

# launch.pyw = launch.py ohne Konsolenfenster
Copy-Item (Join-Path $ScriptDir "launch.py") $LaunchPyw -Force

$WShell = New-Object -ComObject WScript.Shell
$Shortcut = $WShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "pythonw.exe"       # pythonw = kein Konsolenfenster
$Shortcut.Arguments = "`"$LaunchPyw`""
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "HPC ML Dashboard – Uni Kassel Cluster"
$Shortcut.IconLocation = "shell32.dll,14"  # Globus-Icon
$Shortcut.Save()

Write-Host "Shortcut erstellt: $ShortcutPath" -ForegroundColor Green
Write-Host "Doppelklick auf dem Desktop startet das Dashboard."
