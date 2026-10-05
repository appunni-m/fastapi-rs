"""Independent public OpenAPI inputs for retained response fields and schema hooks.

No outcomes are prescribed. Metadata, callbacks and raw ASGI journals are user
code; only normal public FastAPI and Pydantic interfaces generate documents.
"""

import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import Field
from pydantic_core import core_schema


class IndependentJsonSchemaError(ValueError):
    """One ordinary user JSON-schema hook refuses its first selected call."""


def encode_protocol_value(value: Any) -> Any:
    """Preserve all send keys, bytes, ordered headers and container shapes."""
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


class OpenApiJournal:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.warning_records: list[dict[str, Any]] = []
        self.handled_errors: list[dict[str, Any]] = []
        self.core_calls: dict[str, int] = {}
        self.json_calls: dict[str, int] = {}
        self.request_number = 0
        self.stage = "factory:start"
        self.refuse_label: str | None = None
        self.refusals_remaining = 0
        self.last_public_document: Any = None

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
            "warnings": [dict(record) for record in self.warning_records],
            "handled_errors": [dict(error) for error in self.handled_errors],
            "core_calls": dict(self.core_calls),
            "json_calls": dict(self.json_calls),
            "requests": self.request_number,
            "armed_label": self.refuse_label,
            "refusals_remaining": self.refusals_remaining,
        }


@dataclass(frozen=True)
class SchemaProbe:
    journal: OpenApiJournal
    label: str
    schema_ref: str | None = None

    def __get_pydantic_core_schema__(self, source_type: Any, handler: Any) -> Any:
        journal = self.journal
        call = journal.core_calls.get(self.label, 0) + 1
        journal.core_calls[self.label] = call
        journal.record("schema:core", label=self.label, call=call, annotation=source_type.__name__)
        warnings.warn(
            f"independent core schema hook {self.label} call {call}",
            category=UserWarning,
            stacklevel=1,
        )
        if self.schema_ref is not None:
            return core_schema.int_schema(ref=self.schema_ref)
        return handler(source_type)

    def __get_pydantic_json_schema__(self, schema: Any, handler: Any) -> Any:
        journal = self.journal
        call = journal.json_calls.get(self.label, 0) + 1
        journal.json_calls[self.label] = call
        journal.record("schema:json", label=self.label, call=call, mode=handler.mode)
        warnings.warn(
            f"independent JSON schema hook {self.label} call {call}",
            category=UserWarning,
            stacklevel=1,
        )
        if journal.refuse_label == self.label and journal.refusals_remaining:
            journal.refusals_remaining -= 1
            journal.record("schema:json:refuse", label=self.label)
            raise IndependentJsonSchemaError(f"independent JSON schema refusal: {self.label}")
        document = dict(handler(schema))
        document["x-independent-probe"] = {"label": self.label, "mode": handler.mode}
        return document


class ObserveRequests:
    def __init__(self, app: FastAPI, journal: OpenApiJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        # State responses stay selected by the runner without recording themselves
        # recursively into the callback and full-send journal they return.
        if scope.get("type") != "http" or scope.get("path") == "/state":
            await self.app(scope, receive, send)
            return
        journal = self.journal
        previous_stage = journal.stage
        journal.request_number += 1
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
    journal = OpenApiJournal(event_trace)

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

    setup(
        "state:register",
        lambda: app.get("/state", response_model=None, include_in_schema=False)(read_state),
    )

    async def handle_schema_error(
        request: Request, error: IndependentJsonSchemaError
    ) -> JSONResponse:
        error_type = type(error)
        details = {
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "path": request.url.path,
        }
        journal.handled_errors.append(details)
        journal.record("error:handled", **details)
        return JSONResponse(
            details, status_code=409, headers={"x-independent-error": "json-schema"}
        )

    setup(
        "handler:register",
        lambda: app.exception_handler(IndependentJsonSchemaError)(handle_schema_error),
    )

    async def public_document() -> JSONResponse:
        journal.record("document:call")
        document = app.openapi()
        same_document = (
            None
            if journal.last_public_document is None
            else document is journal.last_public_document
        )
        journal.record("document:result", same_as_previous_success=same_document)
        journal.last_public_document = document
        return JSONResponse(document)

    setup(
        "document:register",
        lambda: app.get("/document", response_model=None, include_in_schema=False)(public_document),
    )

    annotations: dict[str, Any] = {}
    for key, declaration in factory_input["models"].items():
        metadata = []
        if "field" in declaration:
            metadata.append(Field(**declaration["field"]))
        metadata.append(SchemaProbe(journal, declaration["label"], declaration.get("schema_ref")))
        annotation_arguments = (int, *metadata)
        annotations[key] = Annotated[annotation_arguments]

    async def probe() -> Any:
        journal.record("endpoint:call")
        return 17

    responses = {}
    for declaration in factory_input["responses"]:
        responses[declaration["status"]] = {
            "description": declaration["description"],
            "model": annotations[declaration["model"]],
        }
    saved = setup(
        "probe:decorator:create",
        lambda: app.get(
            "/probe",
            response_model=annotations[factory_input["primary"]],
            responses=responses,
            name="independent_probe",
            operation_id="independent_probe_operation",
        ),
    )
    journal.record("decorator:saved")
    setup("probe:decorator:attach", lambda: saved(probe))
    journal.record("decorator:attached")
    if factory_input.get("refuse_once") is not None:
        journal.stage = "factory:arm-json-hook"
        journal.refuse_label = factory_input["refuse_once"]
        journal.refusals_remaining = 1
        journal.record("schema:json:armed", label=journal.refuse_label)
    journal.stage = "ready"
    return ObserveRequests(app, journal)
