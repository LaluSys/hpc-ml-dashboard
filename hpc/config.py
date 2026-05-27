import os
import yaml
from pathlib import Path


_DEFAULTS = {
    "cluster": {
        "hostname": "its-cs1.its.uni-kassel.de",
        "username": "",
        "port": 22,
        "remote_workdir": "~/ml-jobs",
    },
    "defaults": {
        "partition": "pub23",
        "time": "02:00:00",
        "mem": "16G",
        "cpus": 4,
        "modules": ["python/3.13.0/gcc-14.2.0"],
    },
}


def load() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    result = _DEFAULTS.copy()
    for section in ("cluster", "defaults"):
        if section in data:
            result[section] = {**_DEFAULTS.get(section, {}), **data[section]}

    # env var overrides (useful for CI/CD)
    if os.environ.get("HPC_HOST"):
        result["cluster"]["hostname"] = os.environ["HPC_HOST"]
    if os.environ.get("HPC_USER"):
        result["cluster"]["username"] = os.environ["HPC_USER"]

    return result
