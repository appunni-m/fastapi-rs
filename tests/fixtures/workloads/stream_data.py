"""Input workload for a finite binary StreamingResponse."""

from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/stream", response_class=StreamingResponse)
    async def stream_bytes() -> AsyncIterator[bytes]:
        yield b"north-"
        yield b"south"

    return app
