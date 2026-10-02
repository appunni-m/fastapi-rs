"""Independent FastAPI GZipMiddleware and streaming-response integration."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(GZipMiddleware, minimum_size=40, compresslevel=4)

    @app.get("/streamed-report")
    async def streamed_report() -> StreamingResponse:
        async def chunks() -> AsyncIterator[bytes]:
            yield b"stream sample alpha: 0123456789\n"
            yield b"stream sample beta: independent bytes\n"
            yield b"stream sample gamma: final record\n"

        return StreamingResponse(chunks(), media_type="text/plain")

    return app
