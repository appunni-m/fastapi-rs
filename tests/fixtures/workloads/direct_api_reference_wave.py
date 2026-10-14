"""Argument bundles for direct API signatures, effects, and return probes."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass
class Record:
    name: str
    count: int


def read_widget(widget_id: int) -> dict[str, int]:
    return {"widget_id": widget_id}


class _ArgumentBundles(Mapping[str, dict[str, object]]):
    _ROUTER_BUNDLE_NAMES = (
        "apirouter-include-router",
        "fastapi-include-router",
        "fastapi-openapi",
    )

    def __init__(self) -> None:
        self._common = {
            "unused": {"args": [], "kwargs": {}},
            "dataclass-record": {"args": [Record(name="foo", count=100)], "kwargs": {}},
            "debug-true": {"args": [], "kwargs": {"debug": True}},
        }
        self._router_bundles: dict[str, dict[str, object]] | None = None

    def __getitem__(self, key: str) -> dict[str, object]:
        if key in self._common:
            return self._common[key]
        if key not in self._ROUTER_BUNDLE_NAMES:
            raise KeyError(key)
        if self._router_bundles is None:
            self._router_bundles = self._create_router_bundles()
        return self._router_bundles[key]

    def __iter__(self) -> Iterator[str]:
        return iter((*self._common, *self._ROUTER_BUNDLE_NAMES))

    def __len__(self) -> int:
        return len(self._common) + len(self._ROUTER_BUNDLE_NAMES)

    @staticmethod
    def _create_router_bundles() -> dict[str, dict[str, object]]:
        child_router = APIRouter()
        child_router.get(
            "/widgets/{widget_id}",
            name="read_widget",
            tags=["leaf"],
        )(read_widget)
        parent_router = APIRouter()
        app = FastAPI(title="Included Router Workflow", version="1.0.0")

        return {
            "apirouter-include-router": {
                "args": [parent_router, child_router],
                "kwargs": {"prefix": "/nested", "tags": ["nested"]},
            },
            "fastapi-include-router": {
                "args": [app, parent_router],
                "kwargs": {"prefix": "/api", "tags": ["api"]},
            },
            "fastapi-openapi": {"args": [app], "kwargs": {}},
        }


def create_argument_bundles() -> Mapping[str, dict[str, object]]:
    return _ArgumentBundles()
