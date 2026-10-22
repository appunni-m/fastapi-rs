"""Argument bundles for FastAPI constructor keyword compatibility."""

from __future__ import annotations

from collections.abc import Mapping


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "debug-true": {"args": [], "kwargs": {"debug": True}},
        "openapi-prefix-removed": {
            "args": [],
            "kwargs": {"openapi_prefix": "/legacy"},
        },
        "arbitrary-extra-keyword": {
            "args": [],
            "kwargs": {"constructor_trace": "opaque-value"},
        },
        "empty-version-openapi-enabled": {"args": [], "kwargs": {"version": ""}},
        "empty-version-openapi-disabled": {
            "args": [],
            "kwargs": {"version": "", "openapi_url": None},
        },
    }
