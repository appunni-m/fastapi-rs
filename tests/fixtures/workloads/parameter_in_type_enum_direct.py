"""Input-only enum lookup operands for ParameterInType direct API parity."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "enum-empty": {"args": [], "kwargs": {}},
        "name-cookie": {"args": ["cookie"], "kwargs": {}},
        "name-header": {"args": ["header"], "kwargs": {}},
        "name-path": {"args": ["path"], "kwargs": {}},
        "name-query": {"args": ["query"], "kwargs": {}},
        "name-invalid": {"args": ["server"], "kwargs": {}},
        "value-cookie": {"args": ["cookie"], "kwargs": {}},
        "value-header": {"args": ["header"], "kwargs": {}},
        "value-path": {"args": ["path"], "kwargs": {}},
        "value-query": {"args": ["query"], "kwargs": {}},
        "value-invalid": {"args": ["server"], "kwargs": {}},
    }
