"""Argument bundles for FastAPI's deprecated parameter keyword observations.

The direct API runner supplies the invocation frame, so warning locations are
relative to that stable runner call site rather than an application file.
"""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Return independent inputs for deprecated parameter factory calls."""
    return {
        "query-example": {
            "args": [],
            "kwargs": {"default": None, "example": "query1"},
        },
        "query-regex": {"args": [], "kwargs": {"regex": "^fixedquery$"}},
        "body-example": {
            "args": [],
            "kwargs": {"example": {"data": "Data in Body example"}},
        },
        "path-example": {"args": [], "kwargs": {"example": "item_1"}},
        "header-example": {
            "args": [],
            "kwargs": {"default": None, "example": "header1"},
        },
        "cookie-example": {
            "args": [],
            "kwargs": {"default": None, "example": "cookie1"},
        },
    }
