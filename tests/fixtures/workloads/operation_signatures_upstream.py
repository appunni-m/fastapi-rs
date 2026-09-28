"""Arguments for public decorator signature probes."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Provide the required empty bundle; signature probes do not call methods."""
    return {"unused": {"args": [], "kwargs": {}}}
