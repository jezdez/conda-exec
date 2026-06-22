"""Tests for the ``ce`` standalone entry point."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda.base.context import context, reset_context

from conda_exec.main import main

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def test_main_no_args(capsys):
    result = main([])
    assert result == 2
    captured = capsys.readouterr()
    assert "missing TOOL argument" in captured.err


def test_main_list_mode(exec_home, capsys):
    result = main(["--list"])
    assert result == 0


def test_main_initializes_conda_context_for_channel_flags(
    exec_home,
    monkeypatch,
    tmp_path,
):
    recorded_channels: tuple[str, ...] | None = None
    condarc = tmp_path / "condarc"
    condarc.write_text("channels:\n  - https://repo.anaconda.com/pkgs/main\n")
    search_path = context._search_path
    argparse_args = context._argparse_args

    def fake_execute(args):
        nonlocal recorded_channels
        recorded_channels = context.channels
        return 0

    monkeypatch.setenv("CONDARC", str(condarc))
    monkeypatch.setattr("conda_exec.main.execute", fake_execute)

    try:
        result = main(["-c", "conda-forge", "ruff"])
    finally:
        reset_context(search_path, argparse_args)

    assert result == 0
    assert recorded_channels == (
        "conda-forge",
        "https://repo.anaconda.com/pkgs/main",
    )


def test_main_dispatches_to_execute(exec_home, solver_calls, monkeypatch):
    from conda.common.compat import on_win
    from conda.common.path import BIN_DIRECTORY

    binary_name = "mytool.exe" if on_win else "mytool"

    def fake_find_binary(prefix, name):
        binary = prefix / BIN_DIRECTORY / binary_name
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("")
        return binary

    monkeypatch.setattr("conda_exec.binaries.find_binary", fake_find_binary)
    monkeypatch.setattr(
        "conda_exec.run.run_in_prefix", lambda prefix, binary, args, **kw: 0
    )

    result = main(["mytool"])
    assert result == 0
    assert len(solver_calls) == 1


def test_main_runs_script_via_shebang(
    write_script: Callable[..., Path],
    script_env: list[dict],
):
    """Simulate shebang invocation: #!/usr/bin/env ce

    The kernel passes the absolute script path as the first argument,
    so ``ce /path/to/script.py`` must detect and run it as a script.
    """
    script = write_script(
        "# /// script\n"
        "# [tool.conda]\n"
        '# dependencies = ["numpy"]\n'
        "# ///\n"
        "print('hello')\n"
    )
    result = main([str(script.resolve())])
    assert result == 0
    assert len(script_env) == 1
    assert "numpy" in script_env[0]["specs"]
