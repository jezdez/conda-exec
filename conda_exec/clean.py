"""Clean cached tool environments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from conda import reporters
from conda.base.context import context
from conda.exceptions import CondaSystemExit
from rich.console import Console
from rich.markup import escape

from .cache import CacheManager
from .format import cache_entries_table, format_size

if TYPE_CHECKING:
    from argparse import Namespace


def execute_clean(args: Namespace, *, console: Console | None = None) -> int:
    """Remove cached tool environments."""
    console = console or Console(highlight=False)
    cache = CacheManager()
    entries = cache.list_cached()

    if not entries:
        console.print("No cached environments to clean.")
        return 0

    dry_run = args.dry_run or context.dry_run
    to_remove = cache.cleanup_candidates(
        entries,
        older_than_days=args.older_than,
        remove_all=args.remove_all,
        tool=args.tool,
    )

    if not to_remove:
        console.print(
            "Nothing to clean. By default, --clean only removes cached "
            f"environments unused for more than {args.older_than} days; "
            "use --all to remove every cached environment."
        )
        return 0

    total_size = sum(entry.size for entry in to_remove)

    if dry_run:
        console.print(
            f"[bold yellow]Would remove[/bold yellow] {len(to_remove)} "
            f"environment(s) [dim]({format_size(total_size)})[/dim]:"
        )
        console.print(cache_entries_table(to_remove, include_key=True))
        return 0

    if not args.yes:
        console.print(
            f"[bold yellow]Will remove[/bold yellow] {len(to_remove)} "
            f"environment(s) [dim]({format_size(total_size)})[/dim]:"
        )
        console.print(cache_entries_table(to_remove, include_key=True))
        try:
            reporters.confirm_yn()
        except (CondaSystemExit, EOFError):
            console.print("Aborted.")
            return 1

    result = cache.remove_entries(to_remove)
    for key in result.removed_keys:
        console.print(f"Removed [bold]{escape(key)}[/bold]")

    console.print(
        f"[bold cyan]Cleaned[/bold cyan] {result.removed_count} "
        f"environment(s) [dim]({format_size(total_size)})[/dim]."
    )
    return 0
