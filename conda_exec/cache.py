"""Ephemeral environment cache management."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .exceptions import SolveError, SolverNotAvailableError

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)

MAX_ENV_NAME_LEN = 200


@dataclass(frozen=True)
class CacheEntry:
    """Metadata for a cached tool environment."""

    key: str
    tool: str
    prefix: Path
    created: datetime | None
    last_modified: datetime | None
    size: int
    package_count: int


class CacheManager:
    """Manages cached conda environments for ephemeral tool execution."""

    def __init__(self, envs_dir: Path | None = None) -> None:
        if envs_dir is None:
            from .paths import envs_dir as _default_envs_dir

            envs_dir = _default_envs_dir()
        self.envs_dir = envs_dir

    def get_or_create(
        self,
        key: str,
        specs: list[str],
        channels: list[str],
    ) -> Path:
        """Return a cached prefix, creating it if it does not exist."""
        prefix = self._prefix_for(key)
        if self.exists(key):
            self._touch(prefix)
            return prefix
        return self.create(key, specs, channels)

    def create(
        self,
        key: str,
        specs: list[str],
        channels: list[str],
    ) -> Path:
        """Create a new cached environment via conda's solver."""
        from conda.base.context import context
        from conda.exceptions import UnsatisfiableError
        from conda.models.channel import Channel
        from conda.models.match_spec import MatchSpec

        solver_backend = context.plugin_manager.get_cached_solver_backend()
        if solver_backend is None:
            raise SolverNotAvailableError

        prefix = self._prefix_for(key)
        prefix.mkdir(parents=True, exist_ok=True)

        channel_objs = [Channel(c) for c in channels]
        match_specs = [MatchSpec(s) for s in specs]

        tool = key.rsplit("--", 1)[0]

        solver = solver_backend(
            str(prefix),
            channel_objs,
            context.subdirs,
            specs_to_add=match_specs,
        )

        try:
            transaction = solver.solve_for_transaction()
        except (UnsatisfiableError, SystemExit) as exc:
            from conda.gateways.disk.delete import rm_rf

            rm_rf(prefix)
            raise SolveError(tool, str(exc)) from exc

        transaction.download_and_extract()
        transaction.execute()

        return prefix

    def exists(self, key: str) -> bool:
        """Check if a cached environment exists (fast stat-only check)."""
        prefix = self._prefix_for(key)
        return prefix.is_dir() and (prefix / "conda-meta").is_dir()

    def remove(self, key: str) -> None:
        """Remove a cached environment."""
        from conda.core.envs_manager import unregister_env
        from conda.gateways.disk.delete import rm_rf

        prefix = self._prefix_for(key)
        if prefix.exists():
            unregister_env(str(prefix))
            rm_rf(prefix)

    def list_cached(self) -> list[CacheEntry]:
        """Enumerate all cached environments with metadata."""
        from conda.core.prefix_data import PrefixData

        if not self.envs_dir.is_dir():
            return []

        entries = []
        for path in sorted(self.envs_dir.iterdir()):
            if not path.is_dir() or "--" not in path.name:
                continue
            conda_meta = path / "conda-meta"
            if not conda_meta.is_dir():
                continue

            tool = path.name.rsplit("--", 1)[0]
            pd = PrefixData(path)
            records = list(pd.iter_records())

            entries.append(
                CacheEntry(
                    key=path.name,
                    tool=tool,
                    prefix=path,
                    created=pd.created,
                    last_modified=pd.last_modified,
                    size=pd.size(),
                    package_count=len(records),
                )
            )
        return entries

    def _prefix_for(self, key: str) -> Path:
        if len(key) > MAX_ENV_NAME_LEN:
            raise ValueError(f"cache key too long: {len(key)} > {MAX_ENV_NAME_LEN}")
        return self.envs_dir / key

    def _touch(self, prefix: Path) -> None:
        """Update the history file mtime for staleness tracking."""
        history = prefix / "conda-meta" / "history"
        if history.exists():
            history.touch()
