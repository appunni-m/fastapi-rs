"""Independent request-body input workloads for tutorial source review."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


class EmbeddedItem(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None


def create_body_tutorial001_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    async def create_item(item: Item):
        return item

    return app


def create_body_fields_tutorial001_app() -> FastAPI:
    app = FastAPI()

    @app.put("/default/items/{item_id}")
    async def update_item_default(
        item_id: int,
        item: EmbeddedItem = Body(embed=True),  # noqa: B008
    ):
        return {"item_id": item_id, "item": item}

    @app.put("/annotated/items/{item_id}")
    async def update_item_annotated(item_id: int, item: Annotated[EmbeddedItem, Body(embed=True)]):
        return {"item_id": item_id, "item": item}

    return app
