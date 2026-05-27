"""Local credential storage in .credentials.yaml (gitignored, never committed)."""
from pathlib import Path

import yaml

_CREDS_FILE = Path(__file__).parent.parent / ".credentials.yaml"


def load() -> dict:
    if _CREDS_FILE.exists():
        with open(_CREDS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def save(username: str, password: str) -> None:
    data = {"username": username, "password": password}
    with open(_CREDS_FILE, "w") as f:
        yaml.dump(data, f)
    _CREDS_FILE.chmod(0o600)  # owner-only read/write


def clear() -> None:
    if _CREDS_FILE.exists():
        _CREDS_FILE.unlink()
