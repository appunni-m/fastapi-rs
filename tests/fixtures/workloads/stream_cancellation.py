"""Independent infinite async streams for cancellation parity."""

import asyncio
from collections.abc import AsyncIterable, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
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

    if factory_input.get("workflow") == "yield-cleanup":

        async def yielded_resource() -> AsyncIterable[str]:
            event_trace.append("resource-open")
            try:
                yield "held"
            finally:
                event_trace.append("resource-close")

        @app.get("/stream-with-yield", response_class=StreamingResponse)
        async def stream_with_yield(
            resource: Annotated[str, Depends(yielded_resource, scope="request")],
        ) -> AsyncIterable[str]:
            yield f"{resource}-0\n"
            event_trace.append("stream-first-yield-consumed")
            await asyncio.Event().wait()

        @app.get("/events")
        async def events() -> dict[str, list[str]]:
            return {"events": event_trace}

    return app
