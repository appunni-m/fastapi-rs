"""Independent ASGI workload for direct responses returned from FastAPI routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class InventoryItem(BaseModel):
    name: str
    added_at: datetime
    note: str | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/inventory/{sku}")
    def replace_inventory_item(sku: str, item: InventoryItem):
        return JSONResponse(content=jsonable_encoder(item))

    return app
