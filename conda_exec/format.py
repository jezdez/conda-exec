"""Formatting utilities for CLI output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.markup import escape
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import datetime

    from .cache import CacheEntry


def format_size(size_bytes: int) -> str:
    """Format a byte count as a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    value = float(size_bytes)
    for unit in ("KB", "MB", "GB", "TB"):
        value /= 1024
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
    raise AssertionError("unreachable")


def format_age(dt: datetime | None) -> str:
    """Format a datetime as a human-readable age string."""
    from datetime import datetime, timezone

    if dt is None:
        return "unknown"

    now = datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    total_seconds = int((now - dt).total_seconds())

    days = total_seconds // 86400
    if days > 1:
        return f"{days} days ago"
    if days == 1:
        return "1 day ago"
    hours = total_seconds // 3600
    if hours > 1:
        return f"{hours} hours ago"
    if hours == 1:
        return "1 hour ago"
    minutes = total_seconds // 60
    if minutes > 1:
        return f"{minutes} minutes ago"
    if minutes == 1:
        return "1 minute ago"
    return "just now"


def cache_entries_table(
    entries: Iterable[CacheEntry],
    *,
    include_key: bool = False,
) -> Table:
    """Build a Rich table for cached environments."""
    table = Table(show_edge=False, pad_edge=False)
    if include_key:
        table.add_column("Environment", style="bold")
        table.add_column("Tool")
    else:
        table.add_column("Tool", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Last used")
    table.add_column("Packages", justify="right")

    for entry in entries:
        row = [
            format_size(entry.size),
            format_age(entry.last_modified),
            str(entry.package_count),
        ]
        if include_key:
            table.add_row(escape(entry.key), escape(entry.tool), *row)
        else:
            table.add_row(escape(entry.tool), *row)

    return table
