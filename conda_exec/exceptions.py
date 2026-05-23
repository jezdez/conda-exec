"""Exceptions for conda-exec."""

from __future__ import annotations

from conda.exceptions import CondaError


class CondaExecError(CondaError):
    """Base exception for conda-exec operations."""


class SolveError(CondaExecError):
    """Raised when dependency resolution fails."""

    def __init__(self, tool: str, detail: str) -> None:
        self.error_message = f"failed to solve environment for '{tool}': {detail}"
        self.hints: list[str] = []
        super().__init__(self.error_message)


class BinaryNotFoundError(CondaExecError):
    """Raised when a binary is not found in the cached environment."""

    def __init__(self, binary: str, prefix_path: str) -> None:
        self.error_message = f"binary '{binary}' not found in {prefix_path}"
        self.hints = [
            f"the package may not provide a '{binary}' executable",
            "check the package contents with 'conda search --info <package>'",
        ]
        super().__init__(self.error_message)


class SolverNotAvailableError(CondaExecError):
    """Raised when conda-rattler-solver is not installed."""

    def __init__(self) -> None:
        self.error_message = "conda-rattler-solver is required but not installed"
        self.hints = [
            "install it with: conda install -n base conda-rattler-solver",
            "or set 'solver: rattler' in your .condarc",
        ]
        super().__init__(self.error_message)
