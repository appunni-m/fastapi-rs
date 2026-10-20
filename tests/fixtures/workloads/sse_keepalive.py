"""Independent async and sync SSE streams that idle across the default ping interval."""

import asyncio
import time
from collections.abc import AsyncIterator, Iterator

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    """Build two independently requested SSE routes with a 17-second idle gap."""
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/stream/async-idle", response_class=EventSourceResponse)
    async def async_idle_stream() -> AsyncIterator[dict[str, str]]:
        yield {"stage": "connected"}
        await asyncio.sleep(17.0)
        yield {"stage": "resumed"}

    @app.get("/stream/sync-idle", response_class=EventSourceResponse)
    def sync_idle_stream() -> Iterator[dict[str, str]]:
        yield {"stage": "connected"}
        time.sleep(17.0)
        yield {"stage": "resumed"}

    return app
