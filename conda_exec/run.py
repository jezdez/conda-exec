"""Subprocess execution for ephemeral tool invocations."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from conda.common.path import BIN_DIRECTORY

if TYPE_CHECKING:
    from pathlib import Path


def run_in_prefix(prefix: Path, binary: Path, args: list[str]) -> int:
    """Execute a binary from a conda prefix with PATH set correctly.

    Prepends the prefix's bin directory to PATH so the tool can find
    sibling executables. Runs the tool directly via subprocess.run
    with no shell, no output capture, and no activation overhead.

    Returns the tool's exit code.
    """
    bin_dir = str(prefix / BIN_DIRECTORY)
    env = os.environ.copy()
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")

    try:
        result = subprocess.run(
            [str(binary), *args],
            env=env,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except FileNotFoundError:
        print(f"conda exec: {binary.name}: command not found", file=sys.stderr)
        return 127
    except PermissionError:
        print(f"conda exec: {binary.name}: permission denied", file=sys.stderr)
        return 126

    return result.returncode
