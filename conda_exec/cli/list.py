"""List cached tool environments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace
    from datetime import datetime


def configure_list_parser(parser: ArgumentParser) -> None:
    """Configure the ``conda exec list`` argument parser."""
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="json_output",
        help="Output as JSON.",
    )


def execute_list(args: Namespace) -> int:
    """List cached tool environments."""
    import json

    from ..cache import CacheManager

    cache = CacheManager()
    entries = cache.list_cached()

    if not entries:
        print("No cached environments.")
        return 0

    if args.json_output:
        data = [
            {
                "tool": e.tool,
                "key": e.key,
                "prefix": str(e.prefix),
                "created": e.created.isoformat() if e.created else None,
                "last_used": e.last_modified.isoformat() if e.last_modified else None,
                "size_bytes": e.size,
                "packages": e.package_count,
            }
            for e in entries
        ]
        print(json.dumps(data, indent=2))
        return 0

    name_width = max(len(e.tool) for e in entries)
    header_width = max(name_width, 4)
    print(f"{'Tool':<{header_width}}  {'Size':>8}  {'Last used':<16}  Packages")
    for entry in entries:
        size = format_size(entry.size)
        last_used = format_age(entry.last_modified)
        print(
            f"{entry.tool:<{header_width}}  {size:>8}  {last_used:<16}  "
            f"{entry.package_count}"
        )
    return 0


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
    delta = now - dt

    if delta.days > 1:
        return f"{delta.days} days ago"
    if delta.days == 1:
        return "1 day ago"
    hours = delta.seconds // 3600
    if hours > 1:
        return f"{hours} hours ago"
    if hours == 1:
        return "1 hour ago"
    minutes = delta.seconds // 60
    if minutes > 1:
        return f"{minutes} minutes ago"
    if minutes == 1:
        return "1 minute ago"
    return "just now"
