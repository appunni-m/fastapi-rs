"""Independent public inputs for response-field lifetime and class provenance.

This unexecuted proposal has no stored outcomes or implementation dispatch. Its
schema hooks, callbacks, setup exception capture and ASGI wrapper are user code.
"""

import warnings
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic_core import core_schema


class UnsupportedReply:
    pass


def encode_protocol_value(value: Any) -> Any:
    """Keep every send field, byte value, header order and container shape."""
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


class ProbeState:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.warning_records: list[dict[str, Any]] = []
        self.request_number = 0
        self.stage = "factory:start"
        self.setup_result: dict[str, Any] | None = None

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

    def retain_warnings(self, records: list[Any], stage: str) -> None:
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
            "requests": self.request_number,
            "setup_result": self.setup_result,
        }


@dataclass(frozen=True)
class ResponseSchemaProbe:
    state: ProbeState
    reject: bool = False

    def __get_pydantic_core_schema__(self, source_type: Any, handler: Any) -> Any:
        self.state.record("schema:build", annotation=source_type.__name__)
        if self.reject:
            raise ValueError("independent response schema rejected")

        def validate(value: Any, info: Any) -> Any:
            self.state.record("response:validate", value_type=type(value).__name__)
            return value

        def serialize(value: Any, info: Any) -> Any:
            self.state.record("response:serialize", mode=info.mode)
            return value

        return core_schema.with_info_after_validator_function(
            validate,
            handler(source_type),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, info_arg=True
            ),
        )


def response_annotation(model_kind: str, state: ProbeState) -> Any:
    if model_kind == "traced-int":
        return Annotated[int, ResponseSchemaProbe(state)]
    if model_kind == "field-int":
        return Annotated[
            int,
            Field(gt=0, alias="unused_input", serialization_alias="unused_output"),
            ResponseSchemaProbe(state),
        ]
    if model_kind == "reject-schema":
        return Annotated[int, ResponseSchemaProbe(state, reject=True)]
    if model_kind == "unsupported":
        return UnsupportedReply
    if model_kind == "field-model":

        class ResponseRecord(BaseModel):
            model_config = ConfigDict(populate_by_name=True)

            reading: Annotated[int, Field(gt=0, serialization_alias="wireReading")]
            label: str = "reserve"
            note: str | None = None
            internal: str = "private"

            @field_validator("reading")
            @classmethod
            def observe_validation(cls, value: int) -> int:
                state.record("response:validate", value_type=type(value).__name__)
                return value

            @field_serializer("reading")
            def observe_serialization(self, value: int, info: Any) -> int:
                state.record(
                    "response:serialize",
                    mode=info.mode,
                    by_alias=info.by_alias,
                    exclude_unset=info.exclude_unset,
                    exclude_defaults=info.exclude_defaults,
                    exclude_none=info.exclude_none,
                )
                return value

        return ResponseRecord

    class MetricRecord(BaseModel):
        number: Annotated[float, Field(serialization_alias="metric")]
        label: str

        @field_validator("number")
        @classmethod
        def observe_validation(cls, value: float) -> float:
            state.record("response:validate", value_type=type(value).__name__)
            return value

        @field_serializer("number")
        def observe_serialization(self, value: float, info: Any) -> float:
            state.record("response:serialize", mode=info.mode, by_alias=info.by_alias)
            return value

    return MetricRecord


def tagged_response_class(state: ProbeState, tag: str) -> type[JSONResponse]:
    class TaggedJSONResponse(JSONResponse):
        def __init__(self, content: Any, *args: Any, **kwargs: Any) -> None:
            state.record("response-class:construct", tag=tag, content_type=type(content).__name__)
            super().__init__(content, *args, **kwargs)
            self.headers["x-response-provenance"] = tag

    return TaggedJSONResponse


class ObserveRequests:
    def __init__(self, app: Any, state: ProbeState) -> None:
        self.app = app
        self.state = state

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http" or not scope.get("path", "").endswith("/probe"):
            await self.app(scope, receive, send)
            return
        state = self.state
        previous_stage = state.stage
        state.stage = "request"
        state.request_number += 1
        state.record("request:enter", path=scope["path"])

        async def observed_send(message: dict[str, Any]) -> None:
            state.record("response:send", message=encode_protocol_value(message))
            await send(message)

        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            try:
                await self.app(scope, receive, observed_send)
            except Exception as error:
                error_type = type(error)
                state.record(
                    "request:raised",
                    exception_class=f"{error_type.__module__}.{error_type.__qualname__}",
                    exception_message=str(error),
                )
                raise
            finally:
                state.retain_warnings(seen, "request")
                state.record("request:exit")
                state.stage = previous_stage


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ObserveRequests:
    state = ProbeState(event_trace)

    def setup(stage: str, operation: Callable[[], Any]) -> Any:
        state.stage = stage
        state.record("setup:enter")
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            try:
                return operation()
            finally:
                state.retain_warnings(seen, stage)
                state.record("setup:exit")

    classes = {
        "json": JSONResponse,
        "tag-app": tagged_response_class(state, "app"),
        "tag-router": tagged_response_class(state, "router"),
        "tag-include": tagged_response_class(state, "include"),
        "tag-route": tagged_response_class(state, "route"),
    }
    app_options: dict[str, Any] = {}
    if "app_class" in factory_input:
        app_options["default_response_class"] = classes[str(factory_input["app_class"])]
    app = setup("app:create", lambda: FastAPI(**app_options))
    model_kind = str(factory_input.get("model", "metric-model"))
    model = setup("model:prepare", lambda: response_annotation(model_kind, state))

    async def probe(request: Request) -> Any:
        state.record("endpoint:call")
        if factory_input.get("return_response"):
            return JSONResponse({"outside_model": "naïve", "reading": "unvalidated"})
        value = request.query_params.get("value", "7")
        if model_kind in {"traced-int", "field-int", "reject-schema", "unsupported"}:
            return int(value)
        if model_kind == "field-model":
            return {"reading": value, "note": None, "internal": "omit", "extra": "drop"}
        number = float("nan") if factory_input.get("nan") else float(value)
        return {"number": number, "label": "naïve", "extra": "drop"}

    route_options: dict[str, Any] = {"response_model": model}
    if "route_class" in factory_input:
        route_class = factory_input["route_class"]
        route_options["response_class"] = None if route_class is None else classes[route_class]
    if model_kind == "field-model":
        route_options.update(
            response_model_include={"reading", "label", "note"},
            response_model_exclude={"label"},
            response_model_by_alias=False,
            response_model_exclude_unset=True,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True,
        )

    def register_probe() -> None:
        if not factory_input.get("include"):
            setup("app:register", lambda: app.get("/probe", **route_options)(probe))
            return
        router_options: dict[str, Any] = {}
        if "router_class" in factory_input:
            router_options["default_response_class"] = classes[str(factory_input["router_class"])]
        router = setup("router:create", lambda: APIRouter(**router_options))
        setup("router:register", lambda: router.get("/probe", **route_options)(probe))
        include_options: dict[str, Any] = {}
        if "include_class" in factory_input:
            include_options["default_response_class"] = classes[str(factory_input["include_class"])]
        setup(
            "app:include-left",
            lambda: app.include_router(router, prefix="/left", **include_options),
        )
        if factory_input.get("include_twice"):
            setup(
                "app:include-right",
                lambda: app.include_router(router, prefix="/right", **include_options),
            )

    if factory_input.get("capture_setup_error"):
        try:
            register_probe()
        except Exception as error:
            error_type = type(error)
            state.setup_result = {
                "outcome": "exception",
                "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
                "exception_message": str(error),
            }
        else:
            state.setup_result = {
                "outcome": "return",
                "exception_class": None,
                "exception_message": None,
            }
    else:
        register_probe()

    async def read_state() -> JSONResponse:
        return JSONResponse(state.snapshot())

    setup(
        "app:register-state",
        lambda: app.get("/state", response_model=None)(read_state),
    )
    state.stage = "ready"
    return ObserveRequests(app, state)
