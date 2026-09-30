"""Small input-only FastAPI Server-Sent Events workload."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None


ITEMS = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]


def create_app() -> FastAPI:
    """Build the documented SSE routes used by the ASGI input fixture."""
    app = FastAPI()

    @app.get("/items/stream-sse-event", response_class=EventSourceResponse)
    async def stream_events() -> AsyncIterator[ServerSentEvent]:
        yield ServerSentEvent(data="hello", event="greeting", id="1")
        yield ServerSentEvent(data={"key": "value"}, event="json-data", id="2")
        yield ServerSentEvent(comment="just a comment")
        yield ServerSentEvent(data="retry-test", retry=5000)

    @app.get("/items/stream", response_class=EventSourceResponse)
    async def stream_models() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item

    @app.get("/items/stream-raw", response_class=EventSourceResponse)
    async def stream_raw_data() -> AsyncIterator[ServerSentEvent]:
        yield ServerSentEvent(raw_data="plain text without quotes")
        yield ServerSentEvent(raw_data="<div>html fragment</div>", event="html")
        yield ServerSentEvent(raw_data="cpu,87.3,1709145600", event="csv")

    return app
