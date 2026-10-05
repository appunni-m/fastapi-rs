"""Independent public inputs for automatic validation-response documentation.

Additional responses are ordinary decorator inputs. Request validation uses the
default FastAPI handlers, and all observations come from actual public responses.
"""

from collections.abc import Callable, Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def encode_protocol_value(value: Any) -> Any:
    """Keep every ASGI send key, byte value and ordered container unchanged."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"python_type": "bytes", "hex": value.hex()}
    if isinstance(value, tuple):
        return {
            "python_type": "tuple",
            "items": [encode_protocol_value(item) for item in value],
        }
    if isinstance(value, list):
        return [encode_protocol_value(item) for item in value]
    if isinstance(value, dict):
        return {key: encode_protocol_value(item) for key, item in value.items()}
    raise TypeError(f"unsupported public protocol value: {type(value).__name__}")


class ValidationDocumentJournal:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.request_number = 0
        self.stage = "factory:start"

    def record(self, phase: str, **fields: Any) -> None:
        self.entries.append(
            {
                "phase": phase,
                "stage": self.stage,
                "request": self.request_number,
                **fields,
            }
        )
        self.events.append(phase)

    def snapshot(self) -> dict[str, Any]:
        return {
            "trace": [dict(entry) for entry in self.entries],
            "events": list(self.events),
            "requests": self.request_number,
        }


class ObserveRequests:
    def __init__(self, app: FastAPI, journal: ValidationDocumentJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http" or scope.get("path") == "/state":
            await self.app(scope, receive, send)
            return
        journal = self.journal
        previous_stage = journal.stage
        journal.request_number += 1
        journal.stage = f"request:{scope['method']} {scope['path']}"
        journal.record(
            "request:enter",
            method=scope["method"],
            path=scope["path"],
            query=encode_protocol_value(scope.get("query_string", b"")),
        )

        async def observed_send(message: dict[str, Any]) -> None:
            journal.record("response:send", message=encode_protocol_value(message))
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
            journal.stage = previous_stage


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ObserveRequests:
    journal = ValidationDocumentJournal(event_trace)

    def setup(stage: str, operation: Callable[[], Any]) -> Any:
        journal.stage = stage
        journal.record("setup:enter")
        try:
            return operation()
        finally:
            journal.record("setup:exit")

    app = setup(
        "app:create",
        lambda: FastAPI(title="Independent Validation Document", version="8.4"),
    )

    async def read_state() -> JSONResponse:
        return JSONResponse(journal.snapshot())

    setup(
        "state:register",
        lambda: app.get("/state", response_model=None, include_in_schema=False)(read_state),
    )

    async def public_document() -> JSONResponse:
        journal.record("document:call")
        document = app.openapi()
        journal.record(
            "document:result",
            document_keys=list(document),
            response_status_order=[
                {
                    "path": path,
                    "method": method,
                    "statuses": list(operation["responses"]),
                }
                for path, path_item in document["paths"].items()
                for method, operation in path_item.items()
                if isinstance(operation, dict) and "responses" in operation
            ],
            schema_order=list(document.get("components", {}).get("schemas", {})),
        )
        return JSONResponse(document)

    setup(
        "document:register",
        lambda: app.get("/document", response_model=None, include_in_schema=False)(public_document),
    )

    async def independent_reading(reading: int) -> JSONResponse:
        journal.record("endpoint:reading", reading=reading)
        return JSONResponse({"reading": reading, "unit": "independent-measure"})

    responses = {
        declaration["status"]: {"description": declaration["description"]}
        for declaration in factory_input["responses"]
    }
    saved = setup(
        "reading:decorator:create",
        lambda: app.get(
            "/reading",
            response_model=None,
            response_description="Independent successful reading",
            responses=responses,
            name="independent_reading",
            operation_id="independent_reading_operation",
        ),
    )
    journal.record("decorator:saved", declared_status_order=list(responses))
    setup("reading:decorator:attach", lambda: saved(independent_reading))
    journal.record("decorator:attached")
    journal.stage = "ready"
    return ObserveRequests(app, journal)
