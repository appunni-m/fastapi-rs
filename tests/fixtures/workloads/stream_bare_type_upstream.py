"""Independent synchronous, asynchronous, and typed JSONL routes."""

from collections.abc import AsyncIterable, Iterable

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    optional: str | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/stream-bare-async")
    async def stream_bare_async() -> AsyncIterable:
        yield {"name": "foo"}

    @app.get("/items/stream-bare-sync")
    def stream_bare_sync() -> Iterable:
        yield {"name": "bar"}

    router = APIRouter()

    @router.get("/events-jsonl", response_model_exclude_none=True)
    async def stream_events_jsonl() -> AsyncIterable[Item]:
        yield Item(name="foo")

    app.include_router(router, prefix="/api")
    return app
