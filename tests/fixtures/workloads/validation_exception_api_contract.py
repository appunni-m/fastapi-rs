"""Input bundles for direct FastAPI validation-exception API probes."""

from __future__ import annotations

from collections.abc import Mapping


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    errors = [
        {
            "type": "missing",
            "loc": ["body", "name"],
            "msg": "Field required",
            "input": None,
        }
    ]
    endpoint_ctx = {
        "function": "create_item",
        "path": "/items",
        "file": "fixture-input.py",
        "line": 17,
    }
    return {
        "unused": {"args": [], "kwargs": {}},
        "request-populated": {
            "args": [errors],
            "kwargs": {"body": {"name": None}, "endpoint_ctx": endpoint_ctx},
        },
        "request-nonmapping-context": {
            "args": [errors],
            "kwargs": {"body": None, "endpoint_ctx": "invalid-context"},
        },
        "websocket-populated": {"args": [errors], "kwargs": {"endpoint_ctx": endpoint_ctx}},
        "websocket-nonmapping-context": {
            "args": [errors],
            "kwargs": {"endpoint_ctx": "invalid-context"},
        },
    }
