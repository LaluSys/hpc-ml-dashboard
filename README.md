# HPC ML Dashboard

Streamlit-Dashboard zum Einreichen und Überwachen von KI-Trainings-Jobs auf dem HPC-Cluster der Universität Kassel (`its-cs1.its.uni-kassel.de`). Funktioniert auf Linux und Windows.

## Voraussetzungen

- Python >= 3.10 lokal installiert
- Zugang zum Uni-Netz (vor Ort oder per VPN)
- Uni-Kennung (`uk...`) und Passwort

## Installation

```bash
git clone https://github.com/DEIN_USERNAME/hpc-ml-dashboard.git
cd hpc-ml-dashboard

# Linux / macOS
bash setup.sh

# Windows (PowerShell als Admin)
.\setup.ps1
```

## Dashboard starten

```bash
# Linux
python launch.py          # oder Doppelklick auf Desktop-Shortcut

# Windows
doppelklick launch.pyw    # kein Terminalfenster
```

Öffnet automatisch http://localhost:8501. Zugangsdaten werden beim ersten Login im Dashboard eingegeben und können dort gespeichert werden.

## Desktop-Shortcut einrichten (einmalig)

```bash
# Linux
bash install_shortcut.sh

# Windows (PowerShell)
.\install_shortcut.ps1
```

## Erste Schritte

1. Im Browser einloggen (Uni-Kennung + Passwort)
2. **Job einreichen** → Template wählen, Ressourcen angeben, Script-Pfad eintragen
3. **Jobs überwachen** → Live-Status, Log-Viewer, Job abbrechen
4. **Dateien** → Daten hoch-/herunterladen

## Cluster-Umgebung (Uni Kassel)

| Komponente | Details |
|---|---|
| Scheduler | SLURM 24.05 |
| Python | `module load python/3.13.0/gcc-14.2.0` |
| PyTorch | 2.7.0 (im Python-3.13-Modul enthalten) |
| CUDA | 12.6 via `module load nvidia-hpc-sdk/25.1/cuda-12.6` |
| Transformers | 4.57.1 (HuggingFace) |
| Storage | GPFS (36 TB) |

## SLURM-Partitionen

| Partition | Nodes | Zeitlimit | Verwendung |
|---|---|---|---|
| `pub23` | 34 | 6 Tage | Standard CPU-Jobs |
| `pub23gpu` | 2 | 6 Tage | GPU-Training |
| `pub12` | 61 | 10 Tage | Lange CPU-Jobs |

## Extras für den Cluster einrichten

Einmalig auf dem Cluster ein venv mit zusätzlichen Paketen anlegen:

```bash
# Auf dem Cluster (per SSH oder als Job):
bash examples/setup_cluster_venv.sh
```

Installiert: `datasets`, `accelerate`, `peft`, `wandb`, `tensorboard` u.a.

## Troubleshooting

**Verbindung schlägt fehl**
- VPN aktiv? (`vpn.uni-kassel.de`)
- Uni-Netz erreichbar?
- Passwort korrekt?

**Job wird nicht gestartet (PENDING)**
- Partition ausgelastet — `sinfo` im Monitor-Tab zeigt freie Nodes
- Zeitlimit oder RAM-Anforderung zu hoch

**GPU nicht erkannt**
- `pub23gpu`-Nodes: GPUs sind physisch vorhanden, aber nicht per SLURM-GRES registriert. Kein `--gres=gpu:1` nötig — einfach `--partition=pub23gpu` setzen. Bei Problemen ITS-Support kontaktieren.
- CUDA-Modul im Template laden: `nvidia-hpc-sdk/25.1/cuda-12.6`

**SSH-Key einrichten (optional, kein Passwort mehr nötig)**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_uni_cluster -N ""
ssh-copy-id -i ~/.ssh/id_uni_cluster.pub uk12345@its-cs1.its.uni-kassel.de
```

## Beitragen

Pull Requests willkommen! Neue Templates in `templates/`, Beispielscripts in `examples/`.
