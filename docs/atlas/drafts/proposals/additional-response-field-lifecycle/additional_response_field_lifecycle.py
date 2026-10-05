"""Independent public inputs for additional response-field lifetimes.

Route and model declarations are ordinary user data. Journals retain actual
core/JSON callbacks, warnings, handled errors and complete ASGI send messages.
"""

import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic_core import core_schema


class IndependentCoreConstructionError(ValueError):
    """One user metadata hook refuses a selected post-setup construction."""


def encode_protocol_value(value: Any) -> Any:
    """Retain every send key, byte, header order and tuple/list distinction."""
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


class LifecycleJournal:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.warning_records: list[dict[str, Any]] = []
        self.core_calls: dict[str, int] = {}
        self.json_calls: dict[str, int] = {}
        self.endpoint_calls: dict[str, int] = {}
        self.handled_errors: list[dict[str, Any]] = []
        self.request_number = 0
        self.stage = "factory:start"
        self.refuse_label: str | None = None
        self.refusals_remaining = 0

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
            "core_calls": dict(self.core_calls),
            "json_calls": dict(self.json_calls),
            "endpoint_calls": dict(self.endpoint_calls),
            "handled_errors": [dict(error) for error in self.handled_errors],
            "warnings": [dict(record) for record in self.warning_records],
            "requests": self.request_number,
            "armed_label": self.refuse_label,
            "refusals_remaining": self.refusals_remaining,
        }


@dataclass(frozen=True)
class SchemaMetadata:
    journal: LifecycleJournal
    label: str
    core_warning: str | None = None

    def __get_pydantic_core_schema__(self, source_type: Any, handler: Any) -> Any:
        journal = self.journal
        journal.core_calls[self.label] = journal.core_calls.get(self.label, 0) + 1
        journal.record(
            "schema:core",
            label=self.label,
            call=journal.core_calls[self.label],
            annotation=source_type.__name__,
        )
        if self.core_warning is not None:
            warnings.warn(self.core_warning, category=UserWarning, stacklevel=1)
        if journal.refuse_label == self.label and journal.refusals_remaining:
            journal.refusals_remaining -= 1
            journal.record("schema:refuse", label=self.label)
            raise IndependentCoreConstructionError(
                f"independent core construction refused {self.label}"
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

    def __get_pydantic_json_schema__(self, schema: Any, handler: Any) -> Any:
        journal = self.journal
        journal.json_calls[self.label] = journal.json_calls.get(self.label, 0) + 1
        journal.record(
            "schema:json",
            label=self.label,
            call=journal.json_calls[self.label],
            mode=handler.mode,
            core_type=schema.get("type"),
        )
        return handler(schema)


class ObserveRequests:
    def __init__(self, app: FastAPI, journal: LifecycleJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        # The earlier state route does not record its body into its own journal.
        # Its entire response remains selected by the canonical runner.
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
    journal = LifecycleJournal(event_trace)

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

    async def handle_core_error(
        request: Request, error: IndependentCoreConstructionError
    ) -> JSONResponse:
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
        lambda: app.exception_handler(IndependentCoreConstructionError)(handle_core_error),
    )

    def model_for(declaration: Mapping[str, Any]) -> Any:
        return Annotated[
            int,
            SchemaMetadata(journal, declaration["label"], declaration.get("core_warning")),
        ]

    def endpoint_for(declaration: Mapping[str, Any]) -> Callable[..., Any]:
        label = declaration["label"]
        default_value = str(declaration["value"])
        returned_response = declaration.get("returned_response")

        async def endpoint(request: Request) -> Any:
            value = request.query_params.get("value", default_value)
            journal.endpoint_calls[label] = journal.endpoint_calls.get(label, 0) + 1
            journal.record("endpoint:call", label=label, path=request.url.path, value=value)
            if returned_response is not None:
                return JSONResponse(
                    {
                        "label": label,
                        "path": request.url.path,
                        "value": value,
                        "outside_declared_integer": ["independent response"],
                    },
                    status_code=returned_response["status"],
                    headers=returned_response["headers"],
                )
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
                child = named_router(declaration["router"])
                prefix = declaration["prefix"]
                setup(
                    f"include:{prefix}",
                    lambda child=child, prefix=prefix: parent.include_router(child, prefix=prefix),
                )
                continue
            label = declaration["label"]
            primary = model_for(declaration["primary"])
            responses = {}
            for extra in declaration["responses"]:
                responses[extra["status"]] = {
                    "description": extra["description"],
                    "model": model_for(extra["model"]),
                }
            endpoint = endpoint_for(declaration)
            method = getattr(parent, str(declaration.get("method", "GET")).lower())
            saved = setup(
                f"decorator:{label}:create",
                lambda declaration=declaration,
                primary=primary,
                responses=responses,
                method=method,
                label=label: method(
                    declaration["path"],
                    response_model=primary,
                    responses=responses,
                    name=label,
                ),
            )
            journal.record("decorator:saved", label=label)
            setup(
                f"decorator:{label}:attach", lambda saved=saved, endpoint=endpoint: saved(endpoint)
            )
            journal.record("decorator:attached", label=label)

    declare_routes(app, factory_input["routes"])
    if factory_input.get("refuse_once") is not None:
        journal.stage = "factory:arm-user-schema-hook"
        journal.refuse_label = factory_input["refuse_once"]
        journal.refusals_remaining = 1
        journal.record("schema:armed", label=journal.refuse_label)
    journal.stage = "ready"
    return ObserveRequests(app, journal)
