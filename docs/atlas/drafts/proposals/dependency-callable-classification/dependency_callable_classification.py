"""Independent public inputs for immutable dependency callable classification."""

import asyncio
import inspect
from collections.abc import AsyncIterator, Callable, Iterator, Mapping
from functools import partial, wraps
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse


class IndependentClassificationError(RuntimeError):
    pass


class ClassificationJournal:
    def __init__(self, event_trace: list[str]) -> None:
        self.events = event_trace
        self.trace: list[str] = []
        self.calls: dict[str, int] = {}

    def value(self, owner: str, seed: int, scale: int) -> dict[str, Any]:
        self.calls[owner] = self.calls.get(owner, 0) + 1
        self.trace.append(f"value:{owner}:{self.calls[owner]}:{seed}:{scale}")
        return {"owner": owner, "seed": seed, "scaled": seed * scale, "call": self.calls[owner]}

    def enter(self, owner: str, seed: int, scale: int) -> dict[str, Any]:
        self.events.append("dependency-enter")
        self.trace.append(f"resource:{owner}:enter")
        return self.value(owner, seed, scale)

    def leave(self, owner: str) -> None:
        self.events.append("dependency-cleanup")
        self.trace.append(f"resource:{owner}:cleanup")

    def snapshot(self) -> dict[str, Any]:
        return {"trace": list(self.trace), "events": list(self.events), "calls": dict(self.calls)}


def method_forwarder(call: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(call)
    def forwarded(self: Any, *args: Any, **kwargs: Any) -> Any:
        self.journal.trace.append("forward:call-method")
        return call(self, *args, **kwargs)

    return forwarded


class CoroutineReader:
    def __init__(self, journal: ClassificationJournal) -> None:
        self.journal = journal

    async def __call__(self, seed: int, scale: int = 3) -> dict[str, Any]:
        self.journal.trace.append("coroutine:instance:start")
        await asyncio.sleep(0)
        return self.journal.value("coroutine-instance", seed, scale)


class ForwardedCoroutineReader(CoroutineReader):
    __call__ = method_forwarder(CoroutineReader.__call__)


class GeneratorReader:
    def __init__(self, journal: ClassificationJournal) -> None:
        self.journal = journal

    def __call__(self, seed: int, scale: int = 3) -> Iterator[dict[str, Any]]:
        value = self.journal.enter("generator-instance", seed, scale)
        try:
            yield value
        except Exception as error:
            self.journal.trace.append(f"resource:generator-instance:error:{type(error).__name__}")
            raise
        finally:
            self.journal.leave("generator-instance")


class ForwardedGeneratorReader(GeneratorReader):
    __call__ = method_forwarder(GeneratorReader.__call__)


class AsyncGeneratorReader:
    def __init__(self, journal: ClassificationJournal) -> None:
        self.journal = journal

    async def __call__(self, seed: int, scale: int = 3) -> AsyncIterator[dict[str, Any]]:
        self.journal.trace.append("async-generator:instance:start")
        await asyncio.sleep(0)
        value = self.journal.enter("async-generator-instance", seed, scale)
        try:
            yield value
        except Exception as error:
            self.journal.trace.append(
                f"resource:async-generator-instance:error:{type(error).__name__}"
            )
            raise
        finally:
            self.journal.leave("async-generator-instance")


class ForwardedAsyncGeneratorReader(AsyncGeneratorReader):
    __call__ = method_forwarder(AsyncGeneratorReader.__call__)


class ResponseBoundaryRecorder:
    def __init__(self, app: Any, journal: ClassificationJournal) -> None:
        self.app = app
        self.journal = journal

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        async def recorded_send(message: dict[str, Any]) -> None:
            if message.get("type") == "http.response.start":
                self.journal.trace.append("response:start")
            elif message.get("type") == "http.response.body" and not message.get(
                "more_body", False
            ):
                self.journal.trace.append("response:body-end")
            await send(message)

        await self.app(scope, receive, recorded_send)


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> Any:
    app = FastAPI()
    journal = ClassificationJournal(event_trace)

    async def coroutine_reader(seed: int, scale: int = 3) -> dict[str, Any]:
        journal.trace.append("coroutine:function:start")
        await asyncio.sleep(0)
        return journal.value("coroutine-function", seed, scale)

    def generator_reader(seed: int, scale: int = 3) -> Iterator[dict[str, Any]]:
        value = journal.enter("generator-function", seed, scale)
        try:
            yield value
        except Exception as error:
            journal.trace.append(f"resource:generator-function:error:{type(error).__name__}")
            raise
        finally:
            journal.leave("generator-function")

    async def async_generator_reader(seed: int, scale: int = 3) -> AsyncIterator[dict[str, Any]]:
        journal.trace.append("async-generator:function:start")
        await asyncio.sleep(0)
        value = journal.enter("async-generator-function", seed, scale)
        try:
            yield value
        except Exception as error:
            journal.trace.append(f"resource:async-generator-function:error:{type(error).__name__}")
            raise
        finally:
            journal.leave("async-generator-function")

    def sync_forwarder(call: Callable[..., Any], label: str) -> Callable[..., Any]:
        @wraps(call)
        def forwarded(*args: Any, **kwargs: Any) -> Any:
            journal.trace.append(f"forward:{label}")
            return call(*args, **kwargs)

        return forwarded

    @wraps(coroutine_reader)
    def scalar_forwarder(seed: int, scale: int = 3) -> int:
        journal.trace.append("forward:scalar-function")
        return journal.value("scalar-forwarder", seed, scale)["scaled"]

    @inspect.markcoroutinefunction
    def marked_scalar_reader(seed: int, scale: int = 3) -> int:
        journal.trace.append("marked-scalar:call")
        return journal.value("marked-scalar", seed, scale)["scaled"]

    @wraps(generator_reader)
    async def async_generator_adapter(*args: Any, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        journal.trace.append("adapter:async-generator:start")
        iterator = generator_reader(*args, **kwargs)
        try:
            for value in iterator:
                await asyncio.sleep(0)
                yield value
        finally:
            iterator.close()
            journal.trace.append("adapter:async-generator:cleanup")

    produced_coroutines: list[Any] = []

    def unmarked_reader(seed: int, scale: int = 3) -> Any:
        journal.trace.append("unmarked:return-coroutine")
        value = coroutine_reader(seed, scale)
        produced_coroutines.append(value)
        return value

    functions = {
        "coroutine": coroutine_reader,
        "sync-generator": generator_reader,
        "async-generator": async_generator_reader,
    }
    instances = {
        "coroutine": CoroutineReader(journal),
        "sync-generator": GeneratorReader(journal),
        "async-generator": AsyncGeneratorReader(journal),
    }
    forwarded_instances = {
        "coroutine": ForwardedCoroutineReader(journal),
        "sync-generator": ForwardedGeneratorReader(journal),
        "async-generator": ForwardedAsyncGeneratorReader(journal),
    }
    kind = factory_input.get("kind", "coroutine")
    form = factory_input.get("form", "wrapped-function")
    if form == "function":
        selected = functions[kind]
    elif form == "instance":
        selected = instances[kind]
    elif form == "wrapped-function":
        selected = sync_forwarder(functions[kind], "function")
    elif form == "wrapped-instance":
        selected = sync_forwarder(instances[kind], "instance")
    elif form == "wrapped-call-method":
        selected = forwarded_instances[kind]
    elif form == "partial-instance":
        selected = partial(instances[kind], 43)
    elif form == "partial-wrapped-function":
        selected = partial(sync_forwarder(functions[kind], "partial-inner"), 47)
    elif form == "async-generator-adapter":
        selected = async_generator_adapter
    elif form == "unmarked":
        selected = unmarked_reader
    elif form == "scalar-forwarder":
        selected = scalar_forwarder
    elif form == "marked-scalar":
        selected = marked_scalar_reader
    else:
        raise ValueError("unknown independent callable form")

    # These identities and wrappers are complete before registration. No action
    # changes __wrapped__, __call__, partial state, markers, or function code.
    selected_declaration = Depends(selected, scope=factory_input.get("scope"))
    uncached_declaration = Depends(selected, use_cache=False, scope=factory_input.get("scope"))

    def projection(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return {"type": type(value).__name__, "value": value}
        result = {
            "type": type(value).__name__,
            "isawaitable": inspect.isawaitable(value),
            "iscoroutine": inspect.iscoroutine(value),
            "isgenerator": inspect.isgenerator(value),
            "isasyncgen": inspect.isasyncgen(value),
            "same_as_produced_coroutine": bool(
                produced_coroutines and value is produced_coroutines[-1]
            ),
        }
        if inspect.iscoroutine(value):
            result["state_before_close"] = inspect.getcoroutinestate(value)
            value.close()
            result["state_after_close"] = inspect.getcoroutinestate(value)
            journal.trace.append("endpoint:closed-returned-coroutine")
        elif inspect.isgenerator(value):
            value.close()
            journal.trace.append("endpoint:closed-returned-generator")
        return result

    @app.get("/single")
    async def read_single(value: Annotated[Any, selected_declaration]) -> dict[str, Any]:
        journal.trace.append("endpoint:single")
        return {"value": projection(value), **journal.snapshot()}

    @app.get("/pair")
    def read_pair(
        first: Annotated[Any, selected_declaration],
        again: Annotated[Any, selected_declaration],
        fresh: Annotated[Any, uncached_declaration],
    ) -> dict[str, Any]:
        journal.trace.append("endpoint:pair")
        return {
            "first": projection(first),
            "again": projection(again),
            "fresh": projection(fresh),
            "same_cached_value": first is again,
            "same_uncached_value": first is fresh,
            **journal.snapshot(),
        }

    def nested_parent(value: Annotated[Any, selected_declaration]) -> dict[str, Any]:
        journal.trace.append("parent:nested")
        return {"child": projection(value)}

    @app.get("/nested")
    async def read_nested(
        parent: Annotated[dict[str, Any], Depends(nested_parent)],
        direct: Annotated[Any, selected_declaration],
    ) -> dict[str, Any]:
        journal.trace.append("endpoint:nested")
        return {"parent": parent, "direct": projection(direct), **journal.snapshot()}

    @app.get("/controls")
    def read_controls(
        plain: Annotated[Any, Depends(coroutine_reader)],
        partial_function: Annotated[Any, Depends(partial(coroutine_reader, 53))],
        partial_method: Annotated[Any, Depends(partial(instances["coroutine"].__call__, 59))],
    ) -> dict[str, Any]:
        journal.trace.append("endpoint:controls")
        return {
            "plain": projection(plain),
            "partial_function": projection(partial_function),
            "partial_method": projection(partial_method),
            **journal.snapshot(),
        }

    @app.get("/yield-controls")
    async def read_yield_controls(
        sync_function: Annotated[Any, Depends(partial(generator_reader, 67))],
        async_function: Annotated[Any, Depends(partial(async_generator_reader, 71))],
        sync_method: Annotated[Any, Depends(partial(instances["sync-generator"].__call__, 73))],
        async_method: Annotated[Any, Depends(partial(instances["async-generator"].__call__, 79))],
    ) -> dict[str, Any]:
        journal.trace.append("endpoint:yield-controls")
        return {
            "sync_function": projection(sync_function),
            "async_function": projection(async_function),
            "sync_method": projection(sync_method),
            "async_method": projection(async_method),
            **journal.snapshot(),
        }

    @app.get("/raise")
    async def raise_after_dependency(value: Annotated[Any, selected_declaration]) -> dict[str, Any]:
        journal.trace.append(f"endpoint:raise:value-type={type(value).__name__}")
        raise IndependentClassificationError("independent endpoint failure after dependency entry")

    async def classification_guard() -> AsyncIterator[dict[str, Any]]:
        value = journal.enter("classification-guard", 0, 1)
        try:
            yield value
        except Exception as error:
            journal.trace.append(
                f"resource:classification-guard:error:{type(error).__module__}.{type(error).__qualname__}"
            )
            raise
        finally:
            journal.leave("classification-guard")

    guard_declaration = Depends(classification_guard, scope="request")

    @app.get("/classified-scalar", dependencies=[guard_declaration])
    async def read_classified_scalar(value: Annotated[Any, selected_declaration]) -> dict[str, Any]:
        journal.trace.append("endpoint:classified-scalar")
        return {"value": projection(value), **journal.snapshot()}

    @app.get("/classifier-recovery", dependencies=[guard_declaration])
    async def read_classifier_recovery(
        value: Annotated[Any, Depends(coroutine_reader)],
    ) -> dict[str, Any]:
        journal.trace.append("endpoint:classifier-recovery")
        return {"value": projection(value), **journal.snapshot()}

    async def classification_error_response(_request: Any, error: Exception) -> JSONResponse:
        error_class = f"{type(error).__module__}.{type(error).__qualname__}"
        journal.trace.append(f"handler:classification-error:{error_class}")
        return JSONResponse(
            status_code=503,
            content={"error": {"class": error_class, "message": str(error)}, **journal.snapshot()},
        )

    app.add_exception_handler(IndependentClassificationError, classification_error_response)
    app.add_exception_handler(TypeError, classification_error_response)

    # Public endpoint-role registrations use the same immutable user protocols.
    app.get("/endpoint-wrapped-function", response_model=None)(
        sync_forwarder(coroutine_reader, "endpoint-function")
    )
    app.get("/endpoint-wrapped-instance", response_model=None)(
        sync_forwarder(instances["coroutine"], "endpoint-instance")
    )
    app.get("/endpoint-partial-instance", response_model=None)(partial(instances["coroutine"], 61))

    def scope_child() -> Iterator[str]:
        yield "independent-function-scoped-child"

    child_declaration = Depends(scope_child, scope="function")

    def scope_parent(child: Annotated[str, child_declaration]) -> Iterator[str]:
        yield f"parent:{child}"

    class ScopeParentReader:
        def __call__(self, prefix: str, child: Annotated[str, child_declaration]) -> Iterator[str]:
            yield f"{prefix}:{child}"

    scope_parents = {
        "wrapped-function": sync_forwarder(scope_parent, "scope-parent"),
        "partial-instance": partial(ScopeParentReader(), "independent-parent"),
    }

    @app.get("/scope-construction", include_in_schema=False)
    def inspect_scope_construction() -> dict[str, Any]:
        outcomes: list[dict[str, Any]] = []
        for parent_form, parent in scope_parents.items():
            for parent_scope in ["request", "function"]:
                candidate = FastAPI()
                declaration = Depends(parent, scope=parent_scope)
                try:

                    def candidate_endpoint(value: Annotated[str, declaration]) -> dict[str, str]:
                        return {"value": value}

                    candidate.get("/candidate")(candidate_endpoint)
                    outcome = {"outcome": "registered"}
                except Exception as error:
                    outcome = {
                        "outcome": "raise",
                        "exception_class": f"{type(error).__module__}.{type(error).__qualname__}",
                        "exception_message": str(error),
                    }
                outcomes.append(
                    {"parent_form": parent_form, "parent_scope": parent_scope, **outcome}
                )
        return {"outcomes": outcomes, **journal.snapshot()}

    @app.get("/state", include_in_schema=False)
    def read_state() -> dict[str, Any]:
        return journal.snapshot()

    return ResponseBoundaryRecorder(app, journal)
