"""Tests for conda_exec.cli.list -- list command and formatting utilities."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from conda_exec.cli.list import (
    configure_list_parser,
    execute_list,
    format_age,
    format_size,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from conda_exec.cache import CacheEntry


def test_list_parser_defaults():
    p = ArgumentParser()
    configure_list_parser(p)
    args = p.parse_args([])
    assert args.json_output is False


def test_list_parser_json():
    p = ArgumentParser()
    configure_list_parser(p)
    args = p.parse_args(["--json"])
    assert args.json_output is True


@pytest.mark.parametrize(
    ("size_bytes", "expected"),
    [
        (0, "0 B"),
        (512, "512 B"),
        (1023, "1023 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1073741824, "1.0 GB"),
        (1099511627776, "1.0 TB"),
    ],
    ids=[
        "zero",
        "bytes-mid",
        "bytes-max",
        "one-kb",
        "fractional-kb",
        "one-mb",
        "one-gb",
        "one-tb",
    ],
)
def test_format_size(size_bytes: int, expected: str):
    assert format_size(size_bytes) == expected


def test_format_age_none():
    assert format_age(None) == "unknown"


@pytest.mark.parametrize(
    ("delta", "expected"),
    [
        (timedelta(seconds=10), "just now"),
        (timedelta(seconds=90), "1 minute ago"),
        (timedelta(minutes=15), "15 minutes ago"),
        (timedelta(hours=1), "1 hour ago"),
        (timedelta(hours=5), "5 hours ago"),
        (timedelta(days=1), "1 day ago"),
        (timedelta(days=42), "42 days ago"),
    ],
    ids=[
        "just-now",
        "one-minute",
        "minutes",
        "one-hour",
        "hours",
        "one-day",
        "days",
    ],
)
def test_format_age(delta: timedelta, expected: str):
    dt = datetime.now(tz=timezone.utc) - delta
    assert format_age(dt) == expected


def test_format_age_naive_datetime():
    dt = datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=3)
    assert format_age(dt) == "3 days ago"


def test_execute_list_empty(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("conda_exec.cache.CacheManager.list_cached", lambda self: [])
    p = ArgumentParser()
    configure_list_parser(p)
    args = p.parse_args([])
    rc = execute_list(args)
    assert rc == 0
    assert "No cached environments." in capsys.readouterr().out


def test_execute_list_table(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    make_entry: Callable[..., CacheEntry],
):
    entries = [
        make_entry(tool="ruff", key="ruff--abcd1234", size=45_000_000, package_count=3),
        make_entry(
            tool="samtools",
            key="samtools--ef567890",
            size=120_000_000,
            package_count=47,
            age_days=3,
        ),
    ]
    monkeypatch.setattr(
        "conda_exec.cache.CacheManager.list_cached", lambda self: entries
    )
    p = ArgumentParser()
    configure_list_parser(p)
    args = p.parse_args([])
    rc = execute_list(args)
    assert rc == 0

    output = capsys.readouterr().out
    assert "Tool" in output
    assert "ruff" in output
    assert "samtools" in output
    assert "42.9 MB" in output
    assert "114.4 MB" in output


def test_execute_list_json(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    make_entry: Callable[..., CacheEntry],
):
    entries = [
        make_entry(tool="ruff", key="ruff--abcd1234"),
    ]
    monkeypatch.setattr(
        "conda_exec.cache.CacheManager.list_cached", lambda self: entries
    )
    p = ArgumentParser()
    configure_list_parser(p)
    args = p.parse_args(["--json"])
    rc = execute_list(args)
    assert rc == 0

    output = capsys.readouterr().out
    data = json.loads(output)
    assert len(data) == 1
    assert data[0]["tool"] == "ruff"
    assert data[0]["key"] == "ruff--abcd1234"
    assert data[0]["size_bytes"] == 45_000_000
    assert data[0]["packages"] == 3
    assert data[0]["created"] is not None
    assert data[0]["last_used"] is not None
