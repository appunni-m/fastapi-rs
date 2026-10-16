"""Argument bundles for FastAPI constructor keyword compatibility."""

from __future__ import annotations

from collections.abc import Mapping


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "debug-true": {"args": [], "kwargs": {"debug": True}},
        "fastapi-extra-kwargs": {
            "args": [],
            "kwargs": {"constructor_trace": "opaque-value"},
        },
    }
