"""Prospective public inputs for endpoint and response-validation worker dispatch.

This file is an unexecuted proposal. It observes user callbacks and ordinary ASGI
messages; it imports no private source implementation or target internals.
"""

import asyncio
from collections.abc import AsyncIterator, Iterator, Mapping
from contextvars import ContextVar
from threading import Lock, get_ident
from typing import Annotated, Any

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BeforeValidator, field_serializer, field_validator
from pydantic_core import PydanticSerializationError


class IndependentWorkerDispatchError(RuntimeError):
    pass


def encode_protocol_value(value: Any) -> Any:
    """Record protocol values without decoding bytes or collapsing containers."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"python_type": "bytes", "hex": value.hex()}
    if isinstance(value, tuple):
        return {"python_type": "tuple", "items": [encode_protocol_value(item) for item in value]}
    if isinstance(value, list):
        return [encode_protocol_value(item) for item in value]
    if isinstance(value, dict):
        return {key: encode_protocol_value(item) for key, item in value.items()}
    raise TypeError(f"unsupported public protocol value: {type(value).__name__}")


class ProbeState:
    def __init__(self, factory_input: Mapping[str, Any], events: list[str]) -> None:
        self.factory_input = factory_input
        self.events = events
        self.entries: list[dict[str, Any]] = []
        self.lock = Lock()
        self.request_count = 0
        self.failure_phase = str(factory_input.get("failure_phase", ""))
        self.context = ContextVar("independent-dispatch-value", default="outside")
        self.loop_thread = ContextVar("independent-dispatch-loop-thread", default=None)
        self.loop = ContextVar("independent-dispatch-loop", default=None)
        self.request_number = ContextVar("independent-dispatch-request", default=0)

    def on_loop(self) -> bool:
        return get_ident() == self.loop_thread.get()

    def record(self, phase: str, write: str | None = None, **fields: Any) -> None:
        before = self.context.get()
        if write is not None:
            self.context.set(write)
        entry = {
            "request": self.request_number.get(),
            "phase": phase,
            "on_loop": self.on_loop(),
            "context_before": before,
            "context_after": self.context.get(),
            **fields,
        }
        with self.lock:
            self.entries.append(entry)
            self.events.append(phase)

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return {
                "trace": [dict(entry) for entry in self.entries],
                "events": list(self.events),
                "requests": self.request_count,
            }

    def maybe_fail(self, phase: str) -> None:
        if self.failure_phase == phase:
            raise IndependentWorkerDispatchError(f"independent failure in {phase}")

    def handoff(self, phase: str) -> None:
        """Allow a synchronous worker callback to round-trip through its loop.

        A callback already on the loop records that relationship and returns.
        It never synchronously waits on the same loop. There are no sleeps,
        elapsed-time assertions, stored outcomes or target identity checks.
        """
        if self.factory_input.get("handoff_phase") != phase:
            return
        if self.on_loop():
            self.record(f"{phase}:handoff-on-loop")
            return

        self.record(f"{phase}:handoff-submit")

        async def loop_probe() -> dict[str, Any]:
            self.record(f"{phase}:handoff-loop", write=f"{phase}:probe-write")
            return {"on_loop": self.on_loop(), "context": self.context.get()}

        loop = self.loop.get()
        if loop is None:
            raise IndependentWorkerDispatchError("callback has no captured request loop")
        observation = asyncio.run_coroutine_threadsafe(loop_probe(), loop).result()
        self.record(
            f"{phase}:handoff-resume",
            probe_on_loop=observation["on_loop"],
            probe_context=observation["context"],
        )


class ObserveRequest:
    """Ordinary user ASGI wrapper establishing each request's loop/context anchor."""

    def __init__(self, app: Any, state: ProbeState) -> None:
        self.app = app
        self.state = state

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        state = self.state
        observe = scope.get("path") == "/probe"
        if observe:
            with state.lock:
                state.request_count += 1
                request_number = state.request_count
        else:
            request_number = 0
        loop_token = state.loop.set(asyncio.get_running_loop())
        thread_token = state.loop_thread.set(get_ident())
        request_token = state.request_number.set(request_number)
        context_token = state.context.set(
            str(state.factory_input.get("context_seed", "request-seed"))
        )
        if observe:
            state.record("request:enter")

        async def observed_send(message: dict[str, Any]) -> None:
            if observe and message["type"] == "http.response.start":
                state.record("response:start", message=encode_protocol_value(message))
            elif observe and message["type"] == "http.response.body":
                state.record("response:body", message=encode_protocol_value(message))
            elif observe:
                state.record("response:other", message=encode_protocol_value(message))
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        except BaseException as error:
            if observe:
                state.record("request:raised", error_type=type(error).__name__)
            raise
        finally:
            if observe:
                state.record("request:exit")
            state.context.reset(context_token)
            state.request_number.reset(request_token)
            state.loop_thread.reset(thread_token)
            state.loop.reset(loop_token)


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> ObserveRequest:
    state = ProbeState(factory_input, event_trace)
    app = FastAPI()

    def dependency_input(value: Any) -> Any:
        state.record("dependency:input-validate")
        return value

    def endpoint_input(value: Any) -> Any:
        state.record("endpoint:input-validate")
        if state.failure_phase == "input":
            raise ValueError("independent input rejection")
        return value

    DependencyNumber = Annotated[int, BeforeValidator(dependency_input)]
    EndpointNumber = Annotated[int, BeforeValidator(endpoint_input)]

    def sync_dependency(seed: DependencyNumber = 5) -> dict[str, Any]:
        state.record("dependency:sync", write="dependency-sync-write")
        state.handoff("dependency")
        state.maybe_fail("dependency")
        return {"seed": seed}

    async def async_dependency(seed: DependencyNumber = 5) -> dict[str, Any]:
        state.record("dependency:async", write="dependency-async-write")
        state.maybe_fail("dependency")
        return {"seed": seed}

    def sync_function_resource() -> Iterator[None]:
        state.record("function:enter-sync", write="function-sync-open")
        try:
            yield None
        except BaseException as error:
            state.record("function:caught-sync", error_type=type(error).__name__)
            raise
        finally:
            state.record("function:exit-sync", write="function-sync-closed")

    async def async_function_resource() -> AsyncIterator[None]:
        state.record("function:enter-async", write="function-async-open")
        try:
            yield None
        except BaseException as error:
            state.record("function:caught-async", error_type=type(error).__name__)
            raise
        finally:
            state.record("function:exit-async", write="function-async-closed")

    def sync_request_resource() -> Iterator[None]:
        state.record("request-resource:enter-sync", write="request-sync-open")
        try:
            yield None
        except BaseException as error:
            state.record("request-resource:caught-sync", error_type=type(error).__name__)
            raise
        finally:
            state.record("request-resource:exit-sync", write="request-sync-closed")

    async def async_request_resource() -> AsyncIterator[None]:
        state.record("request-resource:enter-async", write="request-async-open")
        try:
            yield None
        except BaseException as error:
            state.record("request-resource:caught-async", error_type=type(error).__name__)
            raise
        finally:
            state.record("request-resource:exit-async", write="request-async-closed")

    class ResponseProbe(BaseModel):
        value: str
        number: int
        same_dependency_value: bool | None

        @field_validator("value", mode="before")
        @classmethod
        def validate_value(cls, value: Any) -> Any:
            state.record("response:validate", write="response-validator-write")
            state.handoff("response-validation")
            if state.failure_phase == "response-validation":
                raise ValueError("independent response rejection")
            return value

        @field_serializer("value")
        def serialize_value(self, value: str) -> str:
            state.record("response:serialize", write="response-serializer-write")
            state.maybe_fail("serialization")
            return value

    async def background_probe() -> None:
        state.record("background:async", write="background-write")

    class AwaitablePayload:
        """User value valid through attributes; it creates no coroutine until awaited."""

        def __init__(self, payload: dict[str, Any]) -> None:
            self.value = payload["value"]
            self.number = payload["number"]
            self.same_dependency_value = payload["same_dependency_value"]

        def __await__(self) -> Any:
            async def evaluated() -> dict[str, Any]:
                state.record("returned-awaitable:executed", write="awaitable-write")
                return {
                    "value": self.value,
                    "number": self.number,
                    "same_dependency_value": self.same_dependency_value,
                }

            return evaluated().__await__()

    def output(
        number: int,
        first: dict[str, Any] | None,
        second: dict[str, Any] | None,
        background_tasks: BackgroundTasks,
    ) -> Any:
        state.record("endpoint:call", write="endpoint-write")
        state.handoff("endpoint")
        state.maybe_fail("endpoint")
        if factory_input.get("background", False):
            background_tasks.add_task(background_probe)
        result = {
            "value": str(factory_input.get("value", "ordinary-value")),
            "number": number,
            "same_dependency_value": first is second if first is not None else None,
        }
        if factory_input.get("response_mode") == "response":
            return JSONResponse(result, headers={"X-Independent-Response": "returned"})
        if factory_input.get("response_mode") == "awaitable":
            return AwaitablePayload(result)
        return result

    dependency_kind = factory_input.get("dependency_kind", "none")
    if dependency_kind == "none":

        def sync_endpoint(background_tasks: BackgroundTasks, number: EndpointNumber = 7) -> Any:
            return output(number, None, None, background_tasks)

        async def async_endpoint(
            background_tasks: BackgroundTasks, number: EndpointNumber = 7
        ) -> Any:
            return output(number, None, None, background_tasks)
    elif dependency_kind in {"sync", "async"}:
        dependency = sync_dependency if dependency_kind == "sync" else async_dependency
        first_dependency_marker = Depends(dependency)
        second_dependency_marker = Depends(dependency)

        def sync_endpoint(
            background_tasks: BackgroundTasks,
            first: dict[str, Any] = first_dependency_marker,
            second: dict[str, Any] = second_dependency_marker,
            number: EndpointNumber = 7,
        ) -> Any:
            return output(number, first, second, background_tasks)

        async def async_endpoint(
            background_tasks: BackgroundTasks,
            first: dict[str, Any] = first_dependency_marker,
            second: dict[str, Any] = second_dependency_marker,
            number: EndpointNumber = 7,
        ) -> Any:
            return output(number, first, second, background_tasks)
    else:
        raise ValueError("unknown dependency_kind")

    resources: list[Any] = []
    function_resource_kind = factory_input.get("function_resource_kind", "none")
    if function_resource_kind != "none":
        function_resource = {
            "sync": sync_function_resource,
            "async": async_function_resource,
        }[function_resource_kind]
        resources.append(Depends(function_resource, scope="function"))
    request_resource_kind = factory_input.get("request_resource_kind", "none")
    if request_resource_kind != "none":
        request_resource = {
            "sync": sync_request_resource,
            "async": async_request_resource,
        }[request_resource_kind]
        resources.append(Depends(request_resource, scope="request"))

    endpoint = {
        "sync": sync_endpoint,
        "async": async_endpoint,
    }[factory_input["endpoint_kind"]]
    response_model = None if factory_input.get("response_mode", "none") == "none" else ResponseProbe
    app.get("/probe", response_model=response_model, dependencies=resources)(endpoint)

    @app.exception_handler(IndependentWorkerDispatchError)
    async def independent_error_handler(
        request: Any, error: IndependentWorkerDispatchError
    ) -> JSONResponse:
        state.record("handler:independent", error_type=type(error).__name__)
        return JSONResponse(
            {"error_type": type(error).__name__, "message": str(error)}, status_code=409
        )

    @app.exception_handler(RequestValidationError)
    async def input_error_handler(request: Any, error: RequestValidationError) -> JSONResponse:
        state.record("handler:input-validation", error_type=type(error).__name__)
        return JSONResponse(
            {
                "error_type": type(error).__name__,
                "locations": [list(detail["loc"]) for detail in error.errors()],
                "messages": [detail["msg"] for detail in error.errors()],
                "body": error.body,
            },
            status_code=422,
        )

    @app.exception_handler(ResponseValidationError)
    async def response_error_handler(request: Any, error: ResponseValidationError) -> JSONResponse:
        state.record("handler:response-validation", error_type=type(error).__name__)
        return JSONResponse(
            {
                "error_type": type(error).__name__,
                "locations": [list(detail["loc"]) for detail in error.errors()],
                "messages": [detail["msg"] for detail in error.errors()],
                "body": error.body,
            },
            status_code=409,
        )

    @app.exception_handler(PydanticSerializationError)
    async def serialization_error_handler(
        request: Any, error: PydanticSerializationError
    ) -> JSONResponse:
        state.record("handler:serialization", error_type=type(error).__name__)
        return JSONResponse(
            {"error_type": type(error).__name__, "message": str(error)}, status_code=409
        )

    @app.get("/state", response_model=None)
    async def read_state() -> JSONResponse:
        return JSONResponse(state.snapshot())

    @app.post("/configure/clear", response_model=None)
    async def clear_failure() -> JSONResponse:
        state.failure_phase = ""
        return JSONResponse({"failure_phase": state.failure_phase})

    return ObserveRequest(app, state)
