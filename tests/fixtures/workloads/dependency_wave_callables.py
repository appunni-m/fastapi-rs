"""Input-only routes for callable dependency forms and annotation resolution."""

from collections.abc import AsyncGenerator, Generator
from functools import partial, wraps
from typing import Annotated

from fastapi import Depends, FastAPI
from typing_extensions import TypeAliasType


def _constant_value() -> int:
    return 321


PinnedValue = TypeAliasType("PinnedValue", Annotated[int, Depends(_constant_value)], type_params=())


def _plain_value(value: str) -> str:
    return f"function:{value}"


async def _async_value(value: str) -> str:
    return f"async-function:{value}"


def _yielded_value(value: str) -> Generator[str, None, None]:
    yield f"yield-function:{value}"


async def _async_yielded_value(value: str) -> AsyncGenerator[str, None]:
    yield f"async-yield-function:{value}"


def _resolve_labels() -> list[str]:
    return ["north", "south"]


async def _stringified_annotation(
    labels: "Annotated[list[str], Depends(_resolve_labels)]",
) -> "list[str]":
    return labels


def create_app() -> FastAPI:
    app = FastAPI()

    class PlainReader:
        def __call__(self, value: str) -> str:
            return f"plain:{value}"

    class SyncYieldReader:
        def __call__(self, value: str) -> Generator[str, None, None]:
            yield f"sync-yield:{value}"

    class AsyncReader:
        async def __call__(self, value: str) -> str:
            return f"async:{value}"

    class AsyncYieldReader:
        async def __call__(self, value: str) -> AsyncGenerator[str, None]:
            yield f"async-yield:{value}"

    class ReaderMethods:
        def read(self, value: str) -> str:
            return f"method:{value}"

        async def read_async(self, value: str) -> str:
            return f"async-method:{value}"

        def read_yield(self, value: str) -> Generator[str, None, None]:
            yield f"method-yield:{value}"

        async def read_async_yield(self, value: str) -> AsyncGenerator[str, None]:
            yield f"async-method-yield:{value}"

    plain_reader = PlainReader()
    sync_yield_reader = SyncYieldReader()
    async_reader = AsyncReader()
    async_yield_reader = AsyncYieldReader()
    reader_methods = ReaderMethods()

    @app.get("/class/callables")
    async def class_callables(
        plain: Annotated[str, Depends(plain_reader)],
        sync_yield: Annotated[str, Depends(sync_yield_reader)],
        async_value: Annotated[str, Depends(async_reader)],
        async_yield: Annotated[str, Depends(async_yield_reader)],
    ) -> dict[str, str]:
        return {
            "plain": plain,
            "sync_yield": sync_yield,
            "async": async_value,
            "async_yield": async_yield,
        }

    @app.get("/class/methods")
    async def class_methods(
        plain: Annotated[str, Depends(reader_methods.read)],
        async_value: Annotated[str, Depends(reader_methods.read_async)],
        sync_yield: Annotated[str, Depends(reader_methods.read_yield)],
        async_yield: Annotated[str, Depends(reader_methods.read_async_yield)],
    ) -> list[str]:
        return [plain, async_value, sync_yield, async_yield]

    @app.get("/functions")
    async def function_shapes(
        plain: Annotated[str, Depends(_plain_value)],
        async_value: Annotated[str, Depends(_async_value)],
        sync_yield: Annotated[str, Depends(_yielded_value)],
        async_yield: Annotated[str, Depends(_async_yielded_value)],
    ) -> list[str]:
        return [plain, async_value, sync_yield, async_yield]

    def sync_part(label: str, value: str) -> str:
        return f"{label}:{value}"

    async def async_part(label: str, value: str) -> str:
        return f"{label}:{value}"

    def yielded_part(label: str, value: str) -> Generator[str, None, None]:
        yield f"{label}:{value}"

    fixed_sync = partial(sync_part, "bound-sync")
    fixed_async = partial(async_part, "bound-async")
    fixed_yield = partial(yielded_part, "bound-yield")

    @app.get("/partial")
    async def partial_dependencies(
        sync_value: Annotated[str, Depends(fixed_sync)],
        async_value: Annotated[str, Depends(fixed_async)],
        yielded_value: Annotated[str, Depends(fixed_yield)],
    ) -> list[str]:
        return [sync_value, async_value, yielded_value]

    def preserve_signature(function):
        @wraps(function)
        def forwarding(*args, **kwargs):
            return function(*args, **kwargs)

        return forwarding

    @preserve_signature
    def decorated_lookup(value: str) -> dict[str, str]:
        return {"wrapped": value}

    @app.get("/wrapped")
    async def wrapped_dependency(
        result: Annotated[dict[str, str], Depends(decorated_lookup)],
    ) -> dict[str, str]:
        return result

    @app.get("/pep695")
    async def pep695_dependency(value: PinnedValue) -> str:
        return f"typed:{value}"

    app.add_api_route("/stringified", _stringified_annotation, methods=["GET"])

    return app
