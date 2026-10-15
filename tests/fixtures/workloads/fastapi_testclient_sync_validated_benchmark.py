"""Independent FastAPI request workload matching the pinned benchmark shape."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel


class ItemIn(BaseModel):
    name: str
    value: int


class ItemOut(BaseModel):
    name: str
    value: int
    dep: int


def dep_a():
    return 40


def dep_b(a: Annotated[int, Depends(dep_a)]):
    return a + 2


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build a fresh sync endpoint app for the isolated TestClient case."""
    del factory_input
    del event_trace
    app = FastAPI()

    @app.post("/sync/validated", response_model=ItemOut)
    def sync_validated(
        item: ItemIn,
        dep: Annotated[int, Depends(dep_b)],
    ):
        return ItemOut(name=item.name, value=item.value, dep=dep)

    return app
