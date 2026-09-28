"""ASGI workload for the tagged client generation tutorial example."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


class ResponseMessage(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", response_model=ResponseMessage, tags=["items"])
    async def create_item(item: Item) -> dict[str, str]:
        return {"message": "Item received"}

    @app.get("/items/", response_model=list[Item], tags=["items"])
    async def get_items() -> list[dict[str, str | int]]:
        return [
            {"name": "Plumbus", "price": 3},
            {"name": "Portal Gun", "price": 9001},
        ]

    @app.post("/users/", response_model=ResponseMessage, tags=["users"])
    async def create_user(user: User) -> dict[str, str]:
        return {"message": "User received"}

    return app
