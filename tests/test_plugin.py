"""Tests for conda_exec.plugin."""

from __future__ import annotations

from conda_exec.plugin import conda_subcommands


def test_registers_exec_and_x():
    subcommands = list(conda_subcommands())
    names = [sc.name for sc in subcommands]
    assert "exec" in names
    assert "x" in names


def test_subcommands_have_summary():
    for sc in conda_subcommands():
        assert sc.summary
        assert len(sc.summary) > 10


def test_subcommands_have_action():
    for sc in conda_subcommands():
        assert callable(sc.action)


def test_subcommands_have_configure_parser():
    for sc in conda_subcommands():
        assert callable(sc.configure_parser)


def test_both_aliases_use_same_handler():
    subcommands = list(conda_subcommands())
    actions = {sc.name: sc.action for sc in subcommands}
    assert actions["exec"] is actions["x"]
