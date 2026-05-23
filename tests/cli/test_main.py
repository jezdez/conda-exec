"""Tests for conda_exec.cli.main -- parser configuration and dispatch."""

from __future__ import annotations

from argparse import ArgumentParser

import pytest

from conda_exec.cli.main import configure_parser, execute


@pytest.fixture()
def parser() -> ArgumentParser:
    p = ArgumentParser()
    configure_parser(p)
    return p


def test_parse_bare_tool(parser: ArgumentParser):
    args = parser.parse_args(["ruff"])
    assert args.tool == "ruff"
    assert args.tool_args == []
    assert args.channels is None
    assert args.spec is None
    assert args.with_specs is None


def test_parse_tool_with_args(parser: ArgumentParser):
    args = parser.parse_args(["ruff", "check", "."])
    assert args.tool == "ruff"
    assert args.tool_args == ["check", "."]


def test_parse_tool_with_separator(parser: ArgumentParser):
    args = parser.parse_args(["ruff", "--", "--check", "."])
    assert args.tool == "ruff"
    assert args.tool_args == ["--check", "."]


def test_parse_channel(parser: ArgumentParser):
    args = parser.parse_args(["-c", "bioconda", "samtools"])
    assert args.channels == ["bioconda"]
    assert args.tool == "samtools"


def test_parse_multiple_channels(parser: ArgumentParser):
    args = parser.parse_args(["-c", "bioconda", "-c", "defaults", "samtools"])
    assert args.channels == ["bioconda", "defaults"]


def test_parse_spec(parser: ArgumentParser):
    args = parser.parse_args(["--spec", "ruff>=0.4", "ruff"])
    assert args.spec == "ruff>=0.4"
    assert args.tool == "ruff"


def test_parse_with_specs(parser: ArgumentParser):
    args = parser.parse_args(["--with", "pytest", "--with", "python=3.12", "ruff"])
    assert args.with_specs == ["pytest", "python=3.12"]
    assert args.tool == "ruff"


def test_parse_refresh(parser: ArgumentParser):
    args = parser.parse_args(["--refresh", "ruff"])
    assert args.refresh is True


def test_parse_no_refresh_default(parser: ArgumentParser):
    args = parser.parse_args(["ruff"])
    assert args.refresh is False


def test_parse_all_options(parser: ArgumentParser):
    args = parser.parse_args(
        [
            "-c",
            "bioconda",
            "--spec",
            "ruff>=0.4",
            "--with",
            "pytest",
            "--refresh",
            "ruff",
            "check",
            ".",
        ]
    )
    assert args.channels == ["bioconda"]
    assert args.spec == "ruff>=0.4"
    assert args.with_specs == ["pytest"]
    assert args.refresh is True
    assert args.tool == "ruff"
    assert args.tool_args == ["check", "."]


def test_parse_list_as_tool(parser: ArgumentParser):
    args = parser.parse_args(["list"])
    assert args.tool == "list"
    assert args.tool_args == []


def test_parse_list_json_as_tool_args(parser: ArgumentParser):
    args = parser.parse_args(["list", "--json"])
    assert args.tool == "list"
    assert args.tool_args == ["--json"]


def test_parse_clean_as_tool(parser: ArgumentParser):
    args = parser.parse_args(["clean"])
    assert args.tool == "clean"
    assert args.tool_args == []


def test_parse_clean_all_as_tool_args(parser: ArgumentParser):
    args = parser.parse_args(["clean", "--all"])
    assert args.tool == "clean"
    assert args.tool_args == ["--all"]


def test_parse_clean_with_options_as_tool_args(parser: ArgumentParser):
    args = parser.parse_args(["clean", "--all", "--dry-run", "ruff"])
    assert args.tool == "clean"
    assert args.tool_args == ["--all", "--dry-run", "ruff"]


def test_dispatch_to_list(parser: ArgumentParser, monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(
        "conda_exec.cli.list.execute_list",
        lambda args: (calls.append("list"), 0)[1],
    )
    args = parser.parse_args(["list"])
    rc = execute(args, parser)
    assert rc == 0
    assert calls == ["list"]


def test_dispatch_to_clean(parser: ArgumentParser, monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(
        "conda_exec.cli.clean.execute_clean",
        lambda args: (calls.append("clean"), 0)[1],
    )
    args = parser.parse_args(["clean"])
    rc = execute(args, parser)
    assert rc == 0
    assert calls == ["clean"]


def test_dispatch_to_run(parser: ArgumentParser, monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    monkeypatch.setattr(
        "conda_exec.cli.main.execute_run", lambda args: (calls.append("run"), 0)[1]
    )
    args = parser.parse_args(["ruff"])
    rc = execute(args, parser)
    assert rc == 0
    assert calls == ["run"]


def test_dispatch_list_parses_subcommand_args(
    parser: ArgumentParser, monkeypatch: pytest.MonkeyPatch
):
    received_args: list = []
    monkeypatch.setattr(
        "conda_exec.cli.list.execute_list",
        lambda args: (received_args.append(args), 0)[1],
    )
    args = parser.parse_args(["list", "--json"])
    execute(args, parser)
    assert received_args[0].json_output is True


def test_dispatch_clean_parses_subcommand_args(
    parser: ArgumentParser, monkeypatch: pytest.MonkeyPatch
):
    received_args: list = []
    monkeypatch.setattr(
        "conda_exec.cli.clean.execute_clean",
        lambda args: (received_args.append(args), 0)[1],
    )
    args = parser.parse_args(["clean", "--all", "--dry-run", "ruff"])
    execute(args, parser)
    assert received_args[0].remove_all is True
    assert received_args[0].dry_run is True
    assert received_args[0].tool == "ruff"
