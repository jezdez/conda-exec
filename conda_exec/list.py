"""List cached tool environments."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.console import Console

from .cache import CacheManager
from .format import cache_entries_table

if TYPE_CHECKING:
    from argparse import Namespace


def execute_list(args: Namespace, *, console: Console | None = None) -> int:
    """List cached tool environments."""
    console = console or Console(highlight=False)
    cache = CacheManager()
    entries = cache.list_cached()

    if not entries:
        console.print("No cached environments.")
        return 0

    if args.json_output:
        data = [
            {
                "tool": entry.tool,
                "key": entry.key,
                "prefix": str(entry.prefix),
                "created": entry.created.isoformat() if entry.created else None,
                "last_used": (
                    entry.last_modified.isoformat() if entry.last_modified else None
                ),
                "size_bytes": entry.size,
                "packages": entry.package_count,
            }
            for entry in entries
        ]
        print(json.dumps(data, indent=2))
        return 0

    console.print(cache_entries_table(entries))
    return 0
