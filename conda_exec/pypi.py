"""Optional conda-pypi integration for installing PyPI packages."""

from __future__ import annotations

import importlib.util

PYPI_CHANNEL = "conda-pypi"


def is_available() -> bool:
    """Check whether conda-pypi is installed."""
    return importlib.util.find_spec("conda_pypi") is not None
