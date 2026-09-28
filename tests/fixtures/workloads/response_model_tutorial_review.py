"""Independent FastAPI response-model review workload.

The routes supply fresh inputs for tutorial behaviors missing from the current
response-model workflows. No output values are stored in parity recipes.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Tutorial001ReviewItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


class Tutorial004ReviewItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


class Tutorial005ReviewItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


class Tutorial006ReviewItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


_TUTORIAL004_ITEM = {
    "name": "Citrine",
    "description": None,
    "price": 71.3,
    "tax": 10.5,
    "tags": [],
}

_TUTORIAL005_ITEM = {
    "name": "Cobalt",
    "description": "Independent response-model fixture",
    "price": 83,
    "tax": 6.25,
}

_TUTORIAL006_ITEM = {
    "name": "Quartz",
    "description": "Independent list-based filter fixture",
    "price": 91,
    "tax": 8.75,
}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/tutorial001-explicit/items/", response_model=Tutorial001ReviewItem)
    async def create_explicit_item(item: Tutorial001ReviewItem) -> Tutorial001ReviewItem:
        return item

    @app.post("/tutorial001-inferred/items/")
    async def create_inferred_item(item: Tutorial001ReviewItem) -> Tutorial001ReviewItem:
        return item

    @app.get("/tutorial001-inferred/items/")
    async def list_inferred_items() -> list[Tutorial001ReviewItem]:
        return [
            {"name": "Copper", "price": 18.25},
            {"name": "Iris", "price": 24},
        ]

    @app.get(
        "/tutorial006/items/{item_id}/name",
        response_model=Tutorial006ReviewItem,
        response_model_include=["name", "description"],
    )
    async def read_tutorial006_name(item_id: str) -> dict[str, object]:
        return _TUTORIAL006_ITEM

    @app.get(
        "/tutorial006/items/{item_id}/public",
        response_model=Tutorial006ReviewItem,
        response_model_exclude=["tax"],
    )
    async def read_tutorial006_public(item_id: str) -> dict[str, object]:
        return _TUTORIAL006_ITEM

    @app.get(
        "/tutorial004/items/{item_id}",
        response_model=Tutorial004ReviewItem,
        response_model_exclude_unset=True,
    )
    async def read_tutorial004_item(item_id: str) -> dict[str, object]:
        return _TUTORIAL004_ITEM

    @app.get(
        "/tutorial005/items/{item_id}/name",
        response_model=Tutorial005ReviewItem,
        response_model_include={"name", "description"},
    )
    async def read_tutorial005_name(item_id: str) -> dict[str, object]:
        return _TUTORIAL005_ITEM

    @app.get(
        "/tutorial005/items/{item_id}/public",
        response_model=Tutorial005ReviewItem,
        response_model_exclude={"tax"},
    )
    async def read_tutorial005_public(item_id: str) -> dict[str, object]:
        return _TUTORIAL005_ITEM

    return app
