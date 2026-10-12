"""Independent path, query, and JSON body validation aggregation workload."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    quantity: int


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.post("/items/{item_id}")
    def create_item(item_id: int, quantity: int, item: Item):
        return {"item_id": item_id, "quantity": quantity, "item": item}

    return app
