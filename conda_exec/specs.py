"""Spec normalization and cache key hashing."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def cache_key(tool: str, specs: list[str], channels: list[str]) -> str:
    """Compute a deterministic cache key for a set of specs and channels.

    Returns ``{tool}--{hash}`` where hash is derived from the sorted,
    normalized spec list and channel list.
    """
    from conda.models.match_spec import MatchSpec

    normalized = sorted(str(MatchSpec(s)) for s in specs)
    blob = "|".join(normalized) + "||" + "|".join(sorted(channels))
    h = hashlib.sha256(blob.encode()).hexdigest()[:8]
    return f"{tool}--{h}"


def build_specs(
    tool: str,
    *,
    spec: str | None = None,
    with_specs: list[str] | None = None,
) -> list[str]:
    """Build the full list of specs from CLI arguments.

    The tool name is used as the base spec unless ``--spec`` overrides it.
    ``--with`` specs are appended.
    """
    base = spec if spec else tool
    result = [base]
    if with_specs:
        result.extend(with_specs)
    return result
