"""Independent required integer-array query inputs and complete public wire."""

from collections.abc import Mapping, Sequence
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse


def preserve_wire(value: Any) -> Any:
    """Represent ASGI bytes and container identity without losing any fields."""
    if isinstance(value, bytes):
        return {"kind": "bytes", "data": value.hex()}
    if isinstance(value, tuple):
        return {"kind": "tuple", "data": [preserve_wire(item) for item in value]}
    if isinstance(value, list):
        return {"kind": "list", "data": [preserve_wire(item) for item in value]}
    if isinstance(value, dict):
        return {
            "kind": "dict",
            "data": [[preserve_wire(key), preserve_wire(item)] for key, item in value.items()],
        }
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"cannot record public ASGI value {type(value).__name__}")


class ArrayWireRecorder:
    def __init__(self, app: FastAPI, events: list[str]) -> None:
        self.app = app
        self.events = events
        self.rows: list[dict[str, Any]] = []
        self.request_count = 0
        self.last_public_document: Any = None

    def record(self, event: str, **payload: Any) -> None:
        self.rows.append({"event": event, "request": self.request_count, **payload})
        self.events.append(event)

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        self.request_count += 1
        self.record(
            "enter",
            method=scope["method"],
            path=scope["path"],
            query=preserve_wire(scope["query_string"]),
        )

        async def record_send(message: dict[str, Any]) -> None:
            self.record("send", message=preserve_wire(message))
            await send(message)

        try:
            await self.app(scope, receive, record_send)
        except Exception as error:
            self.record(
                "raised",
                class_name=f"{type(error).__module__}.{type(error).__qualname__}",
                message=str(error),
            )
            raise
        finally:
            self.record("leave")


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ArrayWireRecorder:
    app = FastAPI(title="Cargo Array Wire", version="4.2")
    observed = ArrayWireRecorder(app, event_trace)
    annotation_family = factory_input["annotation_family"]
    observed.record("setup", annotation_family=annotation_family)
    required_query = Query()
    observed.record("query-marker-created")

    def emit_array(cargo_totals: Sequence[int]) -> JSONResponse:
        observed.record(
            "endpoint",
            values=cargo_totals,
            container_type=f"{type(cargo_totals).__module__}.{type(cargo_totals).__qualname__}",
            item_types=[
                f"{type(item).__module__}.{type(item).__qualname__}" for item in cargo_totals
            ],
        )
        observed.record("public-document-call")
        document = app.openapi()
        observed.record(
            "public-document-returned",
            same_previous_object=(
                None
                if observed.last_public_document is None
                else observed.last_public_document is document
            ),
        )
        observed.last_public_document = document
        return JSONResponse(
            {
                "cargo_totals": cargo_totals,
                "document": document,
                "journal": list(observed.rows),
                "event_trace": list(observed.events),
            }
        )

    if annotation_family == "sequence":

        async def read_cargo(cargo_totals: Sequence[int] = required_query) -> JSONResponse:
            return emit_array(cargo_totals)

    elif annotation_family == "list":

        async def read_cargo(cargo_totals: list[int] = required_query) -> JSONResponse:
            return emit_array(cargo_totals)

    else:
        raise ValueError(f"unknown public annotation family {annotation_family}")

    attach = app.get(
        "/cargo",
        response_model=None,
        name="read_cargo",
        operation_id="read_cargo_array_wire",
    )
    observed.record("decorator-retained")
    attach(read_cargo)
    observed.record("route-attached")
    return observed
