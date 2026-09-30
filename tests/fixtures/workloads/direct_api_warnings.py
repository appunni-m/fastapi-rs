"""Argument bundles for FastAPI's deprecated Query keyword observations.

The direct API runner supplies the invocation frame, so warning locations are
relative to that stable runner call site rather than an application file.
"""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Return independent inputs for deprecated `example` and `regex` calls."""
    return {
        "query-example": {"args": [], "kwargs": {"example": "legacy-query-example"}},
        "query-regex": {"args": [], "kwargs": {"regex": "^fixedquery$"}},
    }
