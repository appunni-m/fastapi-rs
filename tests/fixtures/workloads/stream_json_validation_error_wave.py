"""Streaming response values that exercise FastAPI response validation."""

from collections.abc import AsyncIterable, Iterable

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/async")
    async def stream_async() -> AsyncIterable[Item]:
        yield {"name": "valid", "price": 1.0}
        yield {"name": "invalid", "price": "not-a-number"}

    @app.get("/items/sync")
    def stream_sync() -> Iterable[Item]:
        yield {"name": "valid", "price": 1.0}
        yield {"name": "invalid", "price": "not-a-number"}

    return app
