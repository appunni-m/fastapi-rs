"""ASGI workload for the first client generation tutorial example."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


class ResponseMessage(BaseModel):
    message: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", response_model=ResponseMessage)
    async def create_item(item: Item) -> dict[str, str]:
        return {"message": "item received"}

    @app.get("/items/", response_model=list[Item])
    async def get_items() -> list[dict[str, str | int]]:
        return [
            {"name": "Plumbus", "price": 3},
            {"name": "Portal Gun", "price": 9001},
        ]

    return app
