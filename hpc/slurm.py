import io
import posixpath
import re
from datetime import datetime

import pandas as pd

from .connection import SSHConnection


def submit(conn: SSHConnection, script_content: str, job_name: str, workdir: str) -> str:
    """Upload job script via SFTP and submit via sbatch. Returns job ID."""
    sftp = conn.get_sftp()

    logs_dir = posixpath.join(workdir, "logs")
    scripts_dir = posixpath.join(workdir, "scripts")
    for d in (workdir, logs_dir, scripts_dir):
        try:
            sftp.mkdir(d)
        except OSError:
            pass  # already exists

    script_path = posixpath.join(scripts_dir, f"{job_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh")
    with sftp.open(script_path, "w") as f:
        f.write(script_content)
    sftp.chmod(script_path, 0o755)

    stdout, stderr, code = conn.run(f"sbatch {script_path}")
    if code != 0:
        raise RuntimeError(f"sbatch failed: {stderr.strip()}")

    match = re.search(r"Submitted batch job (\d+)", stdout)
    if not match:
        raise RuntimeError(f"Could not parse job ID from: {stdout}")
    return match.group(1)


def list_jobs(conn: SSHConnection, username: str) -> pd.DataFrame:
    """Return DataFrame of current jobs for this user."""
    stdout, _, _ = conn.run(
        f'squeue -u {username} -o "%.10i %.20j %.8T %.10M %.6D %.10P %.12l %.8C %.8m" --noheader'
    )
    rows = []
    for line in stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 9:
            rows.append({
                "JobID": parts[0],
                "Name": parts[1],
                "Status": parts[2],
                "Time": parts[3],
                "Nodes": parts[4],
                "Partition": parts[5],
                "TimeLimit": parts[6],
                "CPUs": parts[7],
                "Memory": parts[8],
            })
    return pd.DataFrame(rows)


def cancel(conn: SSHConnection, job_id: str) -> bool:
    _, stderr, code = conn.run(f"scancel {job_id}")
    return code == 0


def get_log(conn: SSHConnection, job_id: str, workdir: str, tail: int = 150) -> str:
    log_pattern = posixpath.join(workdir, "logs", f"{job_id}_*.out")
    stdout, _, _ = conn.run(f"ls {log_pattern} 2>/dev/null | head -1")
    log_file = stdout.strip()
    if not log_file:
        return f"(Kein Log für Job {job_id} gefunden. Job läuft noch oder wurde noch nicht gestartet.)"
    out, _, _ = conn.run(f"tail -n {tail} {log_file}")
    return out or "(Log leer)"


def get_err(conn: SSHConnection, job_id: str, workdir: str, tail: int = 50) -> str:
    err_pattern = posixpath.join(workdir, "logs", f"{job_id}_*.err")
    stdout, _, _ = conn.run(f"ls {err_pattern} 2>/dev/null | head -1")
    err_file = stdout.strip()
    if not err_file:
        return ""
    out, _, _ = conn.run(f"tail -n {tail} {err_file}")
    return out


def sinfo_summary(conn: SSHConnection) -> pd.DataFrame:
    stdout, _, _ = conn.run('sinfo -o "%.12P %.5a %.10l %.4D %.6t" --noheader')
    rows = []
    seen = set()
    for line in stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 5:
            partition = parts[0].rstrip("*")
            if partition not in seen:
                seen.add(partition)
                rows.append({
                    "Partition": partition,
                    "Avail": parts[1],
                    "TimeLimit": parts[2],
                    "Nodes": parts[3],
                    "State": parts[4],
                })
    return pd.DataFrame(rows)
