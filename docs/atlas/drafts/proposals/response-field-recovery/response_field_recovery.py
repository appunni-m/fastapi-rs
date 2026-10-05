"""Independent public inputs for response-field branch recovery.

This inactive workload accepts ordinary route declarations and user hook
options. Its journals contain actual callback, warning and ASGI observations.
"""

import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic.warnings import UnsupportedFieldAttributeWarning
from pydantic_core import core_schema


class IndependentSchemaConstructionError(ValueError):
    """A user schema hook refuses a construction selected by a public request."""


def encode_protocol_value(value: Any) -> Any:
    """Retain every send field, bytes, header order and tuple/list distinctions."""
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


class RecoveryJournal:
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

    def arm(self, label: str) -> None:
        self.reject_label = label
        self.rejections_remaining = 1
        self.record("schema:armed", label=label)

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
            "armed_label": self.reject_label,
            "rejections_remaining": self.rejections_remaining,
        }


@dataclass(frozen=True)
class ConstructionProbe:
    journal: RecoveryJournal
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
    def __init__(self, app: FastAPI, journal: RecoveryJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        # The earlier public state route does not record its own body into the
        # journal. The canonical runner still observes its full response.
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
    journal = RecoveryJournal(event_trace)

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

    async def arm_hook(request: Request) -> JSONResponse:
        journal.arm(request.query_params["label"])
        return JSONResponse(journal.snapshot())

    setup("state:register", lambda: app.get("/state", response_model=None)(read_state))
    setup("arm:register", lambda: app.post("/arm", response_model=None)(arm_hook))

    warning_categories = {
        "unsupported-field": UnsupportedFieldAttributeWarning,
        "user": UserWarning,
    }

    async def handle_schema_error(
        request: Request, error: IndependentSchemaConstructionError
    ) -> JSONResponse:
        error_type = type(error)
        details = {
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "path": request.url.path,
        }
        journal.handled_errors.append(details)
        journal.record("error:handled", **details)
        for declaration in factory_input.get("handler_warnings", []):
            category = warning_categories[declaration["category"]]
            message = declaration["message"]
            journal.record(
                "handler:warning",
                category=f"{category.__module__}.{category.__qualname__}",
                message=message,
            )
            warnings.warn(message, category=category, stacklevel=1)
        return JSONResponse(details, status_code=409)

    setup(
        "handler:register",
        lambda: app.exception_handler(IndependentSchemaConstructionError)(handle_schema_error),
    )

    def endpoint_for(declaration: Mapping[str, Any]) -> Callable[..., Any]:
        label = declaration["label"]
        default_value = str(declaration["value"])

        async def endpoint(request: Request) -> Any:
            value = request.query_params.get("value", default_value)
            journal.endpoint_calls[label] = journal.endpoint_calls.get(label, 0) + 1
            journal.record("endpoint:call", label=label, value=value)
            return value

        return endpoint

    named_routers: dict[str, APIRouter] = {}

    def named_router(name: str) -> APIRouter:
        if name not in named_routers:
            child = setup(f"router:create:{name}", APIRouter)
            declare_routes(child, factory_input["routers"][name]["routes"])
            named_routers[name] = child
        return named_routers[name]

    def declare_routes(parent: Any, declarations: Sequence[Mapping[str, Any]]) -> None:
        for declaration in declarations:
            if declaration["kind"] == "include":
                prefix = declaration["prefix"]
                if "router" in declaration:
                    child = named_router(declaration["router"])
                else:
                    child = setup(f"router:create:{prefix}", APIRouter)
                    declare_routes(child, declaration["routes"])
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
    journal.stage = "ready"
    return ObserveRequests(app, journal)
