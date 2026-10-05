"""Independent public inputs for generator-based awaitable delegation."""

import asyncio
import inspect
import types
import warnings
from collections.abc import Callable, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse


class IndependentGeneratorAwaitError(Exception):
    """Ordinary user error delivered by an event-loop Future."""


def error_projection(error: BaseException) -> dict[str, str]:
    return {
        "class": f"{type(error).__module__}.{type(error).__qualname__}",
        "message": str(error),
    }


def value_protocol(value: Any) -> dict[str, Any]:
    result = {
        "type": f"{type(value).__module__}.{type(value).__qualname__}",
        "is_generator": inspect.isgenerator(value),
        "is_coroutine": inspect.iscoroutine(value),
        "is_awaitable": inspect.isawaitable(value),
        "has_await_method": hasattr(value, "__await__"),
    }
    if inspect.isgenerator(value):
        result["state"] = inspect.getgeneratorstate(value)
    return result


def send_projection(value: Any) -> Any:
    """Keep message fields, container shapes, bytes and insertion order."""
    if isinstance(value, bytes):
        return {"bytes": value.hex()}
    if isinstance(value, tuple):
        return {"tuple": [send_projection(item) for item in value]}
    if isinstance(value, list):
        return {"list": [send_projection(item) for item in value]}
    if isinstance(value, dict):
        return {"dict": [[key, send_projection(item)] for key, item in value.items()]}
    return value


class Journal:
    def __init__(self, suspension: str, failure: str) -> None:
        self.suspension = suspension
        self.failure = failure
        self.failure_armed = failure != "none"
        self.trace: list[dict[str, Any]] = []
        self.generators: list[tuple[int, str, Any]] = []
        self.futures: list[tuple[int, asyncio.Future[Any]]] = []
        self.sends: list[dict[str, Any]] = []
        self.next_generator = 0
        self.next_request = 0

    def record(self, event: str, **data: Any) -> None:
        self.trace.append({"event": event, **data})

    def allocate(self, role: str, maker: Callable[[int], Any]) -> Any:
        self.next_generator += 1
        number = self.next_generator
        value = maker(number)
        self.generators.append((number, role, value))
        self.record("allocate-generator", number=number, role=role, protocol=value_protocol(value))
        return value

    def close_remaining(self) -> None:
        for number, role, value in self.generators:
            before = inspect.getgeneratorstate(value)
            if before != "GEN_CLOSED":
                value.close()
                self.record(
                    "close-retained-generator",
                    number=number,
                    role=role,
                    before=before,
                    after=inspect.getgeneratorstate(value),
                )

    def snapshot(self) -> dict[str, Any]:
        futures = []
        for number, future in self.futures:
            item = {"number": number, "done": future.done(), "cancelled": future.cancelled()}
            if future.done() and not future.cancelled():
                error = future.exception()
                if error is None:
                    item["result"] = future.result()
                else:
                    item["exception"] = error_projection(error)
            futures.append(item)
        return {
            "failure_armed": self.failure_armed,
            "trace": list(self.trace),
            "generators": [
                {"number": number, "role": role, "protocol": value_protocol(value)}
                for number, role, value in self.generators
            ],
            "futures": futures,
            "sends": list(self.sends),
        }


class RequestObserver:
    def __init__(self, app: Any, journal: Journal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope["path"] == "/state":
            await self.app(scope, receive, send)
            return
        self.journal.next_request += 1
        request = self.journal.next_request
        path = scope["path"]
        self.journal.record("request-enter", request=request, path=path)

        async def observed_send(message: Any) -> None:
            self.journal.sends.append(
                {"request": request, "path": path, "message": send_projection(message)}
            )
            if message["type"] == "http.response.start":
                self.journal.record("response-start", request=request, path=path)
            elif message["type"] == "http.response.body" and not message.get("more_body", False):
                self.journal.record("response-body-end", request=request, path=path)
            await send(message)

        with warnings.catch_warnings(record=True) as observed_warnings:
            warnings.simplefilter("always", DeprecationWarning)
            try:
                await self.app(scope, receive, observed_send)
            finally:
                self.journal.record(
                    "request-warnings",
                    request=request,
                    items=[
                        {
                            "class": f"{item.category.__module__}.{item.category.__qualname__}",
                            "message": str(item.message),
                        }
                        for item in observed_warnings
                    ],
                )
                self.journal.record("request-exit", request=request, path=path)


class IteratorAwaitable:
    def __init__(self, journal: Journal, make_generator: Callable[[], Any]) -> None:
        self.journal = journal
        self.make_generator = make_generator

    def __await__(self) -> Any:
        self.journal.record("await-method", form="ordinary-iterator")
        return self.iterator()

    def iterator(self) -> Any:
        self.journal.record("ordinary-iterator-enter")
        try:
            result = yield from self.make_generator()
            self.journal.record("ordinary-iterator-result", result=result)
            return result
        finally:
            self.journal.record("ordinary-iterator-finally")


class GeneratorReturningAwaitable:
    def __init__(self, journal: Journal, make_generator: Callable[[], Any]) -> None:
        self.journal = journal
        self.make_generator = make_generator

    def __await__(self) -> Any:
        self.journal.record("await-method", form="iterable-coroutine-result")
        return self.make_generator()


class NonIteratorAwaitable:
    def __init__(self, journal: Journal) -> None:
        self.journal = journal

    def __await__(self) -> Any:
        self.journal.record("await-method", form="integer-result")
        return 23


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> Any:
    suspension = factory_input.get("suspension", "future")
    failure = factory_input.get("failure", "none")
    returned_kind = factory_input.get("returned_kind", "iterable")
    journal = Journal(suspension, failure)
    app = FastAPI()

    @types.coroutine
    def legacy_awaitable(seed: int, number: int) -> Any:
        journal.record("iterable-generator-enter", number=number, seed=seed)
        try:
            if journal.suspension == "immediate":
                result = {"seed": seed, "number": number, "value": seed * 7}
            elif journal.suspension == "checkpoint":
                journal.record("checkpoint-yield", number=number)
                received = yield None
                journal.record("checkpoint-resume", number=number, received=received)
                result = {"seed": seed, "number": number, "value": seed * 11}
            elif journal.suspension == "future":
                loop = asyncio.get_running_loop()
                future = loop.create_future()
                journal.futures.append((number, future))

                def complete_future() -> None:
                    journal.record("future-callback", number=number, seed=seed)
                    if journal.failure_armed:
                        future.set_exception(
                            IndependentGeneratorAwaitError(f"future failed for seed {seed}")
                        )
                    else:
                        future.set_result({"seed": seed, "number": number, "value": seed * 13})

                loop.call_soon(complete_future)
                journal.record("future-yield", number=number, done=future.done())
                try:
                    result = yield from future.__await__()
                except IndependentGeneratorAwaitError as error:
                    journal.record("future-error", number=number, error=error_projection(error))
                    if journal.failure != "catch":
                        raise
                    result = {
                        "seed": seed,
                        "number": number,
                        "caught": error_projection(error),
                    }
                journal.record("future-resume", number=number, done=future.done())
            else:
                raise ValueError(f"unknown user suspension {journal.suspension}")
            journal.record("iterable-generator-result", number=number, result=result)
            return result
        finally:
            journal.record("iterable-generator-finally", number=number)

    def plain_generator(seed: int, number: int) -> Any:
        journal.record("plain-generator-enter", number=number, seed=seed)
        try:
            received = yield None
            journal.record("plain-generator-resume", number=number, received=received)
            return {"seed": seed, "number": number, "value": seed * 17}
        finally:
            journal.record("plain-generator-finally", number=number)

    def make_iterable(seed: int, role: str) -> Any:
        return journal.allocate(role, lambda number: legacy_awaitable(seed, number))

    def make_value(seed: int, role: str) -> Any:
        if returned_kind == "iterable":
            return make_iterable(seed, role)
        if returned_kind == "unflagged":
            return journal.allocate(role, lambda number: plain_generator(seed, number))
        if returned_kind == "await-iterator":
            return IteratorAwaitable(journal, lambda: make_iterable(seed, role))
        if returned_kind == "await-generator":
            return GeneratorReturningAwaitable(journal, lambda: make_iterable(seed, role))
        if returned_kind == "await-noniterator":
            return NonIteratorAwaitable(journal)
        raise ValueError(f"unknown user return kind {returned_kind}")

    @inspect.markcoroutinefunction
    def marked_dependency(seed: int = 17) -> Any:
        journal.record("marked-dependency-invoke", seed=seed)
        return make_value(seed, "marked-dependency")

    @inspect.markcoroutinefunction
    def marked_endpoint(seed: int = 17) -> Any:
        journal.record("marked-endpoint-invoke", seed=seed)
        return make_value(seed, "marked-endpoint")

    def raw_dependency(seed: int = 17) -> Any:
        journal.record("unmarked-dependency-invoke", seed=seed)
        return make_iterable(seed, "unmarked-dependency")

    async def bridge_dependency(seed: int = 17) -> Any:
        journal.record("async-bridge-invoke", seed=seed)
        result = await make_iterable(seed, "async-bridge")
        journal.record("async-bridge-result", result=result)
        return result

    async def recovery_dependency(seed: int = 17) -> Any:
        journal.record("recovery-dependency-invoke", seed=seed)
        result = await make_iterable(seed, "recovery-dependency")
        journal.record("recovery-dependency-result", result=result)
        return result

    @types.coroutine
    def declared_yield_dependency(seed: int = 17) -> Any:
        journal.record("declared-yield-enter", seed=seed)
        try:
            yield {"role": "declared-yield", "seed": seed, "value": seed * 19}
        except BaseException as error:
            journal.record("declared-yield-error", error=error_projection(error))
            raise
        finally:
            journal.record("declared-yield-finally", seed=seed)

    async def request_guard() -> Any:
        journal.record("request-guard-enter")
        try:
            yield None
        except BaseException as error:
            journal.record("request-guard-error", error=error_projection(error))
            raise
        finally:
            journal.record("request-guard-finally")

    async def function_guard() -> Any:
        journal.record("function-guard-enter")
        try:
            yield None
        except BaseException as error:
            journal.record("function-guard-error", error=error_projection(error))
            raise
        finally:
            journal.record("function-guard-finally")

    guards = [Depends(request_guard, scope="request"), Depends(function_guard, scope="function")]
    first_marker = Depends(marked_dependency)
    second_marker = Depends(marked_dependency)
    uncached_marker = Depends(marked_dependency, use_cache=False)

    @app.get("/pair", dependencies=guards, response_model=None)
    async def pair(
        first: Annotated[Any, first_marker],
        second: Annotated[Any, second_marker],
        uncached: Annotated[Any, uncached_marker],
    ) -> Any:
        journal.record("pair-endpoint")
        return {
            "first": first,
            "second": second,
            "uncached": uncached,
            "same_cached_value": first is second,
            "same_uncached_value": first is uncached,
        }

    parent_child_marker = Depends(marked_dependency)

    async def parent(value: Annotated[Any, parent_child_marker]) -> Any:
        journal.record("parent-invoke", value=value)
        return value

    parent_marker = Depends(parent)
    later_marker = Depends(marked_dependency)

    @app.get("/nested", dependencies=guards, response_model=None)
    async def nested(
        first: Annotated[Any, parent_marker], later: Annotated[Any, later_marker]
    ) -> Any:
        journal.record("nested-endpoint")
        return {"first": first, "later": later, "same_value": first is later}

    app.get("/endpoint", dependencies=guards, response_model=None)(marked_endpoint)

    bridge_marker = Depends(bridge_dependency)

    @app.get("/bridge", dependencies=guards, response_model=None)
    async def bridge(value: Annotated[Any, bridge_marker]) -> Any:
        journal.record("bridge-endpoint")
        return value

    raw_first_marker = Depends(raw_dependency)
    raw_second_marker = Depends(raw_dependency)

    @app.get("/raw-value", dependencies=guards, response_model=None)
    async def raw_value(
        first: Annotated[Any, raw_first_marker], second: Annotated[Any, raw_second_marker]
    ) -> Any:
        before = value_protocol(first)
        journal.record("raw-value-endpoint", before=before, same_value=first is second)
        if inspect.isgenerator(first):
            first.close()
        after = value_protocol(first)
        journal.record("raw-value-close", after=after)
        return {"before": before, "after": after, "same_value": first is second}

    yield_marker = Depends(declared_yield_dependency)

    @app.get("/direct-yield", dependencies=guards, response_model=None)
    async def direct_yield(value: Annotated[Any, yield_marker]) -> Any:
        journal.record("direct-yield-endpoint", value=value)
        return value

    recovery_marker = Depends(recovery_dependency)

    @app.get("/recovery", dependencies=guards, response_model=None)
    async def recovery(value: Annotated[Any, recovery_marker]) -> Any:
        journal.record("recovery-endpoint")
        return value

    async def error_handler(_request: Any, error: Exception) -> JSONResponse:
        observed = error_projection(error)
        journal.record("error-handler", error=observed)
        return JSONResponse({"error": observed}, status_code=409)

    app.add_exception_handler(TypeError, error_handler)
    app.add_exception_handler(IndependentGeneratorAwaitError, error_handler)

    @app.post("/configure/clear", response_model=None)
    async def clear_failure() -> JSONResponse:
        journal.failure_armed = False
        journal.close_remaining()
        journal.record("clear-failure", failure_armed=journal.failure_armed)
        return JSONResponse({"failure_armed": journal.failure_armed})

    @app.get("/state", response_model=None)
    async def state() -> JSONResponse:
        return JSONResponse(journal.snapshot())

    journal.record(
        "declared-public-callables",
        marked_dependency_coroutine=inspect.iscoroutinefunction(marked_dependency),
        marked_dependency_generator=inspect.isgeneratorfunction(marked_dependency),
        marked_endpoint_coroutine=inspect.iscoroutinefunction(marked_endpoint),
        legacy_generator=inspect.isgeneratorfunction(legacy_awaitable),
        direct_yield_generator=inspect.isgeneratorfunction(declared_yield_dependency),
        raw_dependency_coroutine=inspect.iscoroutinefunction(raw_dependency),
        raw_dependency_generator=inspect.isgeneratorfunction(raw_dependency),
    )
    return RequestObserver(app, journal)
