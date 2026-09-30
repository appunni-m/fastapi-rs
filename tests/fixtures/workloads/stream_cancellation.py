"""Independent infinite async streams for cancellation parity."""

from collections.abc import AsyncIterable, Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/stream-raw", response_class=StreamingResponse)
    async def raw_stream() -> AsyncIterable[str]:
        index = 0
        while True:
            yield f"sample-{index}\n"
            index += 1

    @app.get("/stream-jsonl")
    async def jsonl_stream() -> AsyncIterable[int]:
        index = 0
        while True:
            yield index
            index += 1

    return app
