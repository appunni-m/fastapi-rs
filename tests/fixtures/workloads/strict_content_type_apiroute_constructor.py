"""Input bundle for the direct APIRoute strict Content-Type option."""

from __future__ import annotations

from typing import Any


def endpoint() -> dict[str, int]:
    return {"value": 7}


def create_argument_bundles() -> dict[str, dict[str, Any]]:
    return {
        "lax-strict-content-type-route": {
            "args": ["/strict-content-type", endpoint],
            "kwargs": {"strict_content_type": False},
        },
        "strict-content-type-route": {
            "args": ["/strict-content-type", endpoint],
            "kwargs": {"strict_content_type": True},
        },
    }
