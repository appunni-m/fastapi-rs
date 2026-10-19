"""Input bundles for direct FastAPI validation-exception API probes."""

from __future__ import annotations

from collections.abc import Mapping


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    return {"unused": {"args": [], "kwargs": {}}}
