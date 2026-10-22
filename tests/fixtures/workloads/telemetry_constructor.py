"""Independent FastAPI constructor arguments for the telemetry input recipe."""

from __future__ import annotations

from collections.abc import Mapping

_ARGUMENT_BUNDLES: dict[str, dict[str, object]] = {
    "unused": {"args": [], "kwargs": {}},
    "telemetry-tracing-disabled": {
        "args": [],
        "kwargs": {"telemetry": {"tracing": False}},
    },
    "telemetry-operation-spans-disabled": {
        "args": [],
        "kwargs": {"telemetry": {"operation_spans": False}},
    },
    "telemetry-signals-disabled": {
        "args": [],
        "kwargs": {
            "telemetry": {
                "tracing": False,
                "metrics": False,
                "logs": False,
                "operation_spans": False,
                "auto_configure": False,
            }
        },
    },
}


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    """Return input-only constructor arguments; the recipe stores no outputs."""
    return _ARGUMENT_BUNDLES
