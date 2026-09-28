"""Input-only workloads adapted from FastAPI 0.141.1 SSE tutorials 001–005.

Source mapping notes: ASGI workflow v2 observes HTTP status, response headers,
and the fully collected response body for stream actions, plus selected
OpenAPI JSON pointers. It does not observe ASGI send or chunk boundaries,
15-second ping timing, warning or log output, or runtime-specific details.
"""

from collections.abc import AsyncIterable, Iterable
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel


def create_tutorial001_app() -> FastAPI:
    app = FastAPI()

    class Item(BaseModel):
        name: str
        description: str | None

    items = [
        Item(name="Plumbus", description="A multi-purpose household device."),
        Item(name="Portal Gun", description="A portal opening device."),
        Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
    ]

    @app.get("/items/stream", response_class=EventSourceResponse)
    async def sse_items() -> AsyncIterable[Item]:
        for item in items:
            yield item

    @app.get("/items/stream-no-async", response_class=EventSourceResponse)
    def sse_items_no_async() -> Iterable[Item]:
        yield from items

    @app.get("/items/stream-no-annotation", response_class=EventSourceResponse)
    async def sse_items_no_annotation():
        for item in items:
            yield item

    @app.get(
        "/items/stream-no-async-no-annotation",
        response_class=EventSourceResponse,
    )
    def sse_items_no_async_no_annotation():
        yield from items

    return app


def create_tutorial002_app() -> FastAPI:
    app = FastAPI()

    class Item(BaseModel):
        name: str
        price: float

    items = [
        Item(name="Plumbus", price=32.99),
        Item(name="Portal Gun", price=999.99),
        Item(name="Meeseeks Box", price=49.99),
    ]

    @app.get("/items/stream", response_class=EventSourceResponse)
    async def stream_items() -> AsyncIterable[ServerSentEvent]:
        yield ServerSentEvent(comment="stream of item updates")
        for index, item in enumerate(items):
            yield ServerSentEvent(
                data=item,
                event="item_update",
                id=str(index + 1),
                retry=5000,
            )

    return app


def create_tutorial003_app() -> FastAPI:
    app = FastAPI()

    @app.get("/logs/stream", response_class=EventSourceResponse)
    async def stream_logs() -> AsyncIterable[ServerSentEvent]:
        logs = [
            "2025-01-01 INFO  Application started",
            "2025-01-01 DEBUG Connected to database",
            "2025-01-01 WARN  High memory usage detected",
        ]
        for log_line in logs:
            yield ServerSentEvent(raw_data=log_line)

    return app


def create_tutorial004_app() -> FastAPI:
    app = FastAPI()

    class Item(BaseModel):
        name: str
        price: float

    items = [
        Item(name="Plumbus", price=32.99),
        Item(name="Portal Gun", price=999.99),
        Item(name="Meeseeks Box", price=49.99),
    ]

    @app.get("/items/stream", response_class=EventSourceResponse)
    async def stream_items(
        last_event_id: Annotated[int | None, Header()] = None,
    ) -> AsyncIterable[ServerSentEvent]:
        start = last_event_id + 1 if last_event_id is not None else 0
        for index, item in enumerate(items):
            if index < start:
                continue
            yield ServerSentEvent(data=item, id=str(index))

    return app


def create_tutorial005_app() -> FastAPI:
    app = FastAPI()

    class Prompt(BaseModel):
        text: str

    @app.post("/chat/stream", response_class=EventSourceResponse)
    async def stream_chat(prompt: Prompt) -> AsyncIterable[ServerSentEvent]:
        for word in prompt.text.split():
            yield ServerSentEvent(data=word, event="token")
        yield ServerSentEvent(raw_data="[DONE]", event="done")

    return app
