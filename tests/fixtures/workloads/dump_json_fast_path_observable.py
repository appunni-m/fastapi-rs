"""Compare the observable response for inferred and explicit JSON response classes."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class InventoryEntry(BaseModel):
    title: str
    cost: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/inferred")
    def get_inferred() -> InventoryEntry:
        return InventoryEntry(title="field-notebook", cost=14.25)

    @app.get("/explicit", response_class=JSONResponse)
    def get_explicit() -> InventoryEntry:
        return InventoryEntry(title="field-notebook", cost=14.25)

    return app
