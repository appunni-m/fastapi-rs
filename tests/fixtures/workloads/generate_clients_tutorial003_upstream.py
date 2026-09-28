"""ASGI workload for custom operation IDs in the client generation example."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


class ResponseMessage(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: str


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def create_app() -> FastAPI:
    app = FastAPI(generate_unique_id_function=custom_generate_unique_id)

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
