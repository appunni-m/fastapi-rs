"""Independent public default-bearing query fields and complete document wire."""

from collections.abc import Mapping
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse


def protocol_value(value: Any) -> Any:
    """Retain ordered ASGI containers, every send key and exact byte contents."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"python_type": "bytes", "hex": value.hex()}
    if isinstance(value, tuple):
        return {"python_type": "tuple", "items": [protocol_value(item) for item in value]}
    if isinstance(value, list):
        return [protocol_value(item) for item in value]
    if isinstance(value, dict):
        return {key: protocol_value(item) for key, item in value.items()}
    raise TypeError(f"unsupported public protocol value: {type(value).__name__}")


class QueryWireJournal:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.request_number = 0
        self.previous_document: Any = None

    def record(self, phase: str, **fields: Any) -> None:
        self.entries.append({"phase": phase, "request": self.request_number, **fields})
        self.events.append(phase)

    def snapshot(self) -> dict[str, Any]:
        return {
            "entries": [dict(entry) for entry in self.entries],
            "events": list(self.events),
            "requests": self.request_number,
        }


class ObserveWire:
    def __init__(self, app: FastAPI, journal: QueryWireJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        journal = self.journal
        journal.request_number += 1
        journal.record(
            "request:enter",
            method=scope["method"],
            path=scope["path"],
            query=protocol_value(scope.get("query_string", b"")),
        )

        async def observed_send(message: dict[str, Any]) -> None:
            journal.record("response:send", message=protocol_value(message))
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        except Exception as error:
            error_type = type(error)
            journal.record(
                "request:raised",
                exception_class=f"{error_type.__module__}.{error_type.__qualname__}",
                exception_message=str(error),
            )
            raise
        finally:
            journal.record("request:exit")


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ObserveWire:
    journal = QueryWireJournal(event_trace)
    placement = factory_input["placement"]
    journal.record("setup:app:create", placement=placement)
    app = FastAPI(title="Independent Query Field Wire", version="3.7")

    def endpoint_response(values: dict[str, Any]) -> JSONResponse:
        journal.record(
            "endpoint:values",
            values=values,
            value_types={
                name: f"{type(value).__module__}.{type(value).__qualname__}"
                for name, value in values.items()
            },
        )
        journal.record("document:public-call")
        document = app.openapi()
        journal.record(
            "document:public-result",
            document_keys=list(document),
            same_object_as_previous=(
                None if journal.previous_document is None else document is journal.previous_document
            ),
        )
        journal.previous_document = document
        return JSONResponse({"values": values, "document": document, "journal": journal.snapshot()})

    if placement == "direct":

        async def independent_observation(
            offset_mark: int = 13,
            batch_width: int = 29,
            term: str = "",
            spare_number: int | None = None,
            spare_word: str | None = None,
        ) -> JSONResponse:
            return endpoint_response(
                {
                    "offset_mark": offset_mark,
                    "batch_width": batch_width,
                    "term": term,
                    "spare_number": spare_number,
                    "spare_word": spare_word,
                }
            )

    elif placement == "dependency":

        async def independent_query_values(
            offset_mark: int = 13,
            batch_width: int = 29,
            term: str = "",
            spare_number: int | None = None,
            spare_word: str | None = None,
        ) -> dict[str, Any]:
            values = {
                "offset_mark": offset_mark,
                "batch_width": batch_width,
                "term": term,
                "spare_number": spare_number,
                "spare_word": spare_word,
            }
            journal.record("dependency:values", values=values)
            return values

        query_marker = Depends(independent_query_values)

        async def independent_observation(values: dict[str, Any] = query_marker) -> JSONResponse:
            return endpoint_response(values)

    else:
        raise ValueError(f"unsupported public placement: {placement}")

    journal.record("setup:decorator:create")
    saved = app.get(
        "/observe",
        response_model=None,
        name="independent_observation",
        operation_id="independent_query_wire_observation",
    )
    journal.record("setup:decorator:retained")
    saved(independent_observation)
    journal.record("setup:decorator:attached")
    return ObserveWire(app, journal)
