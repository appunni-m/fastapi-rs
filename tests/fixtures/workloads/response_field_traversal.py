"""Independent public inputs for lazy response-field traversal and recovery.

This inactive draft constructs ordinary routing trees from declarative user
options. It never reads a case identifier, implementation identity or route
cache, and it contains no prescribed outcomes.
"""

import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic_core import core_schema


class IndependentSchemaConstructionError(ValueError):
    """A user schema hook refuses one selected construction after setup."""


def encode_protocol_value(value: Any) -> Any:
    """Retain bytes, header order, tuple/list shape and every ASGI send field."""
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


class TraversalJournal:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.warning_records: list[dict[str, Any]] = []
        self.schema_calls: dict[str, int] = {}
        self.endpoint_calls: dict[str, int] = {}
        self.handled_errors: list[dict[str, Any]] = []
        self.request_number = 0
        self.stage = "factory:start"
        self.reject_label: str | None = None
        self.rejections_remaining = 0

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

    def retain_warnings(self, records: Sequence[Any], stage: str) -> None:
        for record in records:
            category = record.category
            self.warning_records.append(
                {
                    "stage": stage,
                    "request": self.request_number,
                    "category": f"{category.__module__}.{category.__qualname__}",
                    "message": str(record.message),
                }
            )

    def snapshot(self) -> dict[str, Any]:
        return {
            "trace": [dict(entry) for entry in self.entries],
            "events": list(self.events),
            "schema_calls": dict(self.schema_calls),
            "endpoint_calls": dict(self.endpoint_calls),
            "handled_errors": [dict(error) for error in self.handled_errors],
            "warnings": [dict(record) for record in self.warning_records],
            "requests": self.request_number,
            "rejections_remaining": self.rejections_remaining,
        }


@dataclass(frozen=True)
class ConstructionProbe:
    journal: TraversalJournal
    label: str

    def __get_pydantic_core_schema__(self, source_type: Any, handler: Any) -> Any:
        journal = self.journal
        journal.schema_calls[self.label] = journal.schema_calls.get(self.label, 0) + 1
        journal.record(
            "schema:build",
            label=self.label,
            call=journal.schema_calls[self.label],
            annotation=source_type.__name__,
        )
        if journal.reject_label == self.label and journal.rejections_remaining:
            journal.rejections_remaining -= 1
            journal.record("schema:reject", label=self.label)
            raise IndependentSchemaConstructionError(
                f"independent schema construction refused {self.label}"
            )

        def validate(value: Any, info: Any) -> Any:
            journal.record("response:validate", label=self.label, value=value)
            return value

        def serialize(value: Any, info: Any) -> Any:
            journal.record("response:serialize", label=self.label, value=value, mode=info.mode)
            return value

        return core_schema.with_info_after_validator_function(
            validate,
            handler(source_type),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, info_arg=True
            ),
        )


class ObserveRequests:
    def __init__(self, app: FastAPI, journal: TraversalJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        # A state read is an ordinary earlier full route match. Its own body is
        # excluded from the recorder so snapshots cannot recursively grow.
        if scope.get("type") != "http" or scope.get("path") == "/state":
            await self.app(scope, receive, send)
            return
        journal = self.journal
        journal.request_number += 1
        previous_stage = journal.stage
        journal.stage = f"request:{scope['method']} {scope['path']}"
        journal.record("request:enter", method=scope["method"], path=scope["path"])

        async def observed_send(message: dict[str, Any]) -> None:
            journal.record("response:send", message=encode_protocol_value(message))
            await send(message)

        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
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
                journal.retain_warnings(seen, journal.stage)
                journal.record("request:exit")
                journal.stage = previous_stage


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ObserveRequests:
    journal = TraversalJournal(event_trace)

    def setup(stage: str, operation: Callable[[], Any]) -> Any:
        journal.stage = stage
        journal.record("setup:enter")
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            try:
                return operation()
            finally:
                journal.retain_warnings(seen, stage)
                journal.record("setup:exit")

    app = setup("app:create", FastAPI)

    async def read_state() -> JSONResponse:
        return JSONResponse(journal.snapshot())

    setup("state:register", lambda: app.get("/state", response_model=None)(read_state))

    async def handle_schema_error(
        request: Request, error: IndependentSchemaConstructionError
    ) -> Any:
        error_type = type(error)
        details = {
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "path": request.url.path,
        }
        journal.handled_errors.append(details)
        journal.record("error:handled", **details)
        return JSONResponse(details, status_code=409)

    setup(
        "handler:register",
        lambda: app.exception_handler(IndependentSchemaConstructionError)(handle_schema_error),
    )

    def endpoint_for(declaration: Mapping[str, Any]) -> Callable[..., Any]:
        label = declaration["label"]
        default_value = str(declaration["value"])
        return_response = bool(declaration.get("return_response"))

        async def endpoint(request: Request) -> Any:
            value = request.query_params.get("value", default_value)
            journal.endpoint_calls[label] = journal.endpoint_calls.get(label, 0) + 1
            journal.record("endpoint:call", label=label, value=value)
            if return_response:
                return JSONResponse(
                    {"label": label, "outside_model": "naïve", "value": value},
                    status_code=202,
                    headers={"x-protocol-source": label},
                )
            return value

        return endpoint

    def declare_routes(parent: Any, declarations: Sequence[Mapping[str, Any]]) -> None:
        for declaration in declarations:
            if declaration["kind"] == "include":
                child = setup("router:create", APIRouter)
                declare_routes(child, declaration["routes"])
                prefix = declaration["prefix"]
                setup(
                    f"include:{prefix}",
                    lambda child=child, prefix=prefix: parent.include_router(child, prefix=prefix),
                )
                continue
            label = declaration["label"]
            annotation = Annotated[int, ConstructionProbe(journal, label)]
            endpoint = endpoint_for(declaration)
            method = getattr(parent, str(declaration.get("method", "GET")).lower())
            setup(
                f"route:{label}",
                lambda declaration=declaration,
                annotation=annotation,
                endpoint=endpoint,
                method=method,
                label=label: method(declaration["path"], response_model=annotation, name=label)(
                    endpoint
                ),
            )

    declare_routes(app, factory_input["routes"])
    if factory_input.get("reject_once") is not None:
        journal.reject_label = factory_input["reject_once"]
        journal.rejections_remaining = 1
        journal.stage = "factory:arm-user-hook"
        journal.record("schema:armed", label=journal.reject_label)
    journal.stage = "ready"
    return ObserveRequests(app, journal)
