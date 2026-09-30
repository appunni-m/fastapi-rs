"""Small input-only FastAPI Server-Sent Events workload."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.responses import EventSourceResponse, Response
from fastapi.sse import ServerSentEvent, format_sse_event
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None


ITEMS = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]


def _construct_invalid_event(factory_input: dict[str, Any]) -> None:
    """Exercise one invalid public event construction from input parameters."""
    validation = factory_input["validation"]
    if validation == "null-id":
        ServerSentEvent(data="test", id=factory_input["value"])
    elif validation == "single-line-field":
        ServerSentEvent(
            data="test",
            **{factory_input["field_name"]: factory_input["value"]},
        )
    elif validation == "negative-retry":
        ServerSentEvent(data="test", retry=factory_input["value"])
    elif validation == "float-retry":
        ServerSentEvent(data="test", retry=factory_input["value"])
    elif validation == "mutually-exclusive-data":
        ServerSentEvent(
            data=factory_input["data"],
            raw_data=factory_input["raw_data"],
        )
    else:
        raise ValueError("unsupported SSE validation input")


def _create_format_app(factory_input: dict[str, Any]) -> FastAPI:
    """Expose exact formatter calls as response bodies for ASGI observation."""
    app = FastAPI()

    for case in factory_input["data_cases"]:
        data_str = case["data_str"]

        @app.get(f"/format-data/{case['case_id']}", include_in_schema=False)
        def format_data(data_str: str = data_str) -> Response:
            return Response(
                content=format_sse_event(data_str=data_str),
                media_type="text/event-stream",
            )

    for case in factory_input["comment_cases"]:
        comment = case["comment"]

        @app.get(f"/format-comment/{case['case_id']}", include_in_schema=False)
        def format_comment(comment: str = comment) -> Response:
            return Response(
                content=format_sse_event(comment=comment),
                media_type="text/event-stream",
            )

    return app


def _create_default_app_response_class_app() -> FastAPI:
    app = FastAPI(default_response_class=EventSourceResponse)
    router = APIRouter()

    @router.get("/stream")
    async def stream() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item

    app.include_router(router, prefix="/api")
    return app


def _create_default_parent_router_app() -> FastAPI:
    app = FastAPI()
    parent_router = APIRouter(default_response_class=EventSourceResponse)
    child_router = APIRouter()

    @child_router.get("/stream")
    async def stream() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item

    parent_router.include_router(child_router)
    app.include_router(parent_router, prefix="/api")
    return app


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build routes selected by the independent workflow input."""
    del event_trace
    if "validation" in factory_input:
        _construct_invalid_event(factory_input)
        return FastAPI()

    variant = factory_input.get("variant", "routes")
    if variant == "formatter":
        return _create_format_app(factory_input)
    if variant == "default-app-response-class":
        return _create_default_app_response_class_app()
    if variant == "default-parent-router-response-class":
        return _create_default_parent_router_app()
    if variant != "routes":
        raise ValueError("unsupported SSE workload variant")

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

    @app.get("/items/stream-sync", response_class=EventSourceResponse)
    def stream_models_sync() -> Iterable[Item]:
        yield from ITEMS

    @app.get("/items/stream-no-annotation", response_class=EventSourceResponse)
    async def stream_models_no_annotation():
        for item in ITEMS:
            yield item

    @app.get("/items/stream-sync-no-annotation", response_class=EventSourceResponse)
    def stream_models_sync_no_annotation():
        yield from ITEMS

    @app.get("/items/stream-dict", response_class=EventSourceResponse)
    async def stream_dicts():
        for item in ITEMS:
            yield {"name": item.name, "description": item.description}

    @app.get("/items/stream-mixed", response_class=EventSourceResponse)
    async def stream_mixed() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item
        yield ServerSentEvent(data="custom-event", event="special")
        yield ITEMS[1]

    @app.get("/items/stream-string", response_class=EventSourceResponse)
    async def stream_string():
        yield ServerSentEvent(data="plain text data")

    @app.post("/items/stream-post", response_class=EventSourceResponse)
    async def stream_post() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item

    @app.get("/items/stream-raw", response_class=EventSourceResponse)
    async def stream_raw_data() -> AsyncIterator[ServerSentEvent]:
        yield ServerSentEvent(raw_data="plain text without quotes")
        yield ServerSentEvent(raw_data="<div>html fragment</div>", event="html")
        yield ServerSentEvent(raw_data="cpu,87.3,1709145600", event="csv")

    router = APIRouter()

    @router.get("/events", response_class=EventSourceResponse)
    async def router_events():
        yield {"msg": "hello"}
        yield {"msg": "world"}

    @router.get("/events-typed", response_class=EventSourceResponse)
    async def router_events_typed() -> AsyncIterator[Item]:
        for item in ITEMS:
            yield item

    app.include_router(router, prefix="/api")
    return app
