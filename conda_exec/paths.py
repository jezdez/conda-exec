"""Filesystem layout for conda-exec cached environments."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from platformdirs import user_data_path


@lru_cache(maxsize=1)
def data_dir() -> Path:
    """Return the base data directory for conda-exec.

    Resolution order:
    1. ``CONDA_EXEC_HOME`` environment variable (explicit override)
    2. ``<user_data_dir>/conda/exec/`` via platformdirs
    """
    env = os.environ.get("CONDA_EXEC_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return user_data_path("conda") / "exec"


def envs_dir() -> Path:
    """Return the directory for cached tool environments."""
    return data_dir() / "envs"
