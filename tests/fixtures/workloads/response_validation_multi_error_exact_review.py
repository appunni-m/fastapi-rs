"""Independent workload for aggregated response-validation failures."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float | None = None
    owner_ids: list[int] | None = None


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/items/innerinvalid", response_model=Item)
    def get_innerinvalid():
        return {
            "name": "double invalid",
            "price": "foo",
            "owner_ids": ["foo", "bar"],
        }

    return app
