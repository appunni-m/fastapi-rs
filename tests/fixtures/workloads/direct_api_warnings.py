"""Argument bundles for FastAPI's deprecated parameter keyword observations.

The direct API runner supplies the invocation frame, so warning locations are
relative to that stable runner call site rather than an application file.
"""

from __future__ import annotations

from types import SimpleNamespace


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Return independent inputs for deprecated direct API calls."""
    return {
        "query-example": {
            "args": [],
            "kwargs": {"default": None, "example": "query1"},
        },
        "query-regex": {"args": [], "kwargs": {"regex": "^fixedquery$"}},
        "path-regex": {"args": [], "kwargs": {"regex": "^fixedpath$"}},
        "header-regex": {"args": [], "kwargs": {"regex": "^fixedheader$"}},
        "cookie-regex": {"args": [], "kwargs": {"regex": "^fixedcookie$"}},
        "body-regex": {"args": [], "kwargs": {"regex": "^fixedbody$"}},
        "form-regex": {"args": [], "kwargs": {"regex": "^fixedform$"}},
        "file-regex": {"args": [], "kwargs": {"regex": "^fixedfile$"}},
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
        "operation-id-explicit": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id="explicit-operation",
                    name="ignored_name",
                    path_format="/ignored/{value}",
                ),
                "method": "GET",
            },
        },
        "operation-id-fallback": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id=None,
                    name="read_item",
                    path_format="/items/{item_id}",
                ),
                "method": "POST",
            },
        },
        "operation-id-for-path": {
            "args": [],
            "kwargs": {
                "name": "read-item",
                "path": "/v1/items/{item_id}",
                "method": "PATCH",
            },
        },
    }
