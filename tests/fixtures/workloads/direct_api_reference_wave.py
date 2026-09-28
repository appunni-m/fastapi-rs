"""Argument bundles for direct API signatures and JSON-safe return probes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Record:
    name: str
    count: int


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "dataclass-record": {"args": [Record(name="foo", count=100)], "kwargs": {}},
    }
