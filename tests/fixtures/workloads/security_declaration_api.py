"""Input bundles for FastAPI.Security's public declaration surface."""

from __future__ import annotations


def get_principal() -> dict[str, str]:
    return {"principal": "demo"}


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "scoped-declaration": {
            "args": [],
            "kwargs": {
                "dependency": get_principal,
                "scopes": ["records:read"],
                "use_cache": False,
            },
        },
    }
