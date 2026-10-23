"""Argument bundles for FastAPI's deprecated API observations.

Warning filename and line are part of the parity contract. FastAPI 0.157.0
attributes the root File warning to `param_functions.py:2355`.
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
        "form-example": {"args": [], "kwargs": {"example": "form1"}},
        "file-example": {"args": [], "kwargs": {"example": "file1"}},
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
        "operation-id-empty-string": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id="",
                    name="empty_id",
                    path_format="/items/{item_id}",
                ),
                "method": "PATCH",
            },
        },
        "operation-id-missing-operation-id": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(name="read_item", path_format="/items"),
                "method": "GET",
            },
        },
        "operation-id-missing-path-format": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(operation_id=None, name="read_item"),
                "method": "GET",
            },
        },
        "operation-id-missing-name": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id=None,
                    path_format="/items/{item_id}",
                ),
                "method": "GET",
            },
        },
        "operation-id-invalid-method": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id=None,
                    name="read_item",
                    path_format="/items",
                ),
                "method": 42,
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
        "operation-id-for-path-invalid-method": {
            "args": [],
            "kwargs": {"name": "read-item", "path": "/v1/items", "method": 42},
        },
        "operation-id-explicit-numeric": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id=17,
                    name=None,
                    path_format=None,
                ),
                "method": "GET",
            },
        },
        "operation-id-fallback-non-string-values": {
            "args": [],
            "kwargs": {
                "route": SimpleNamespace(
                    operation_id=0,
                    name=17,
                    path_format=None,
                ),
                "method": "GET",
            },
        },
        "operation-id-for-path-non-string-values": {
            "args": [],
            "kwargs": {"name": 17, "path": None, "method": "GET"},
        },
    }
