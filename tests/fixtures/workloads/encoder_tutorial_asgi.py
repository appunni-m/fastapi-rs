"""Independent request workload for the FastAPI JSON encoder tutorial app."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


def create_app() -> FastAPI:
    item_store: dict[str, dict[str, object]] = {}
    app = FastAPI()

    @app.put("/items/{id}")
    def update_item(id: str, item: Item):
        item_store[id] = jsonable_encoder(item)

    return app
