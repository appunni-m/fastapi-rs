"""Independent endpoint workload for partial-wrapped generator callables."""

from collections.abc import AsyncIterator, Iterator
from functools import partial

from fastapi import FastAPI


class SyncGeneratorEndpoint:
    def __call__(self, label: str) -> Iterator[str]:
        yield label
        yield f"{label}-done"


class AsyncGeneratorEndpoint:
    async def __call__(self, label: str) -> AsyncIterator[str]:
        yield label
        yield f"{label}-done"


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()
    app.get("/sync")(partial(SyncGeneratorEndpoint(), "sync"))
    app.get("/async")(partial(AsyncGeneratorEndpoint(), "async"))
    return app
