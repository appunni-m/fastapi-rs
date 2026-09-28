"""Independent StreamingResponse workloads for FastAPI's stream-data tutorials.

The route shapes mirror the public async/sync, annotated/unannotated generator
forms. Payloads are workload inputs; the companion recipes contain requests and
observation selectors only.
"""

import struct
import zlib
from collections.abc import AsyncIterable, Iterable

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

_TEXT_CHUNKS = ("north signal", "south signal")


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    length = struct.pack(">I", len(data))
    checksum = struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return length + kind + data + checksum


def _png_chunks() -> tuple[bytes, ...]:
    header = struct.pack(">IIBBBBB", 2, 1, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00\x20\x40\x60\xff\x80\xa0\xc0\xff")
    return (
        b"\x89PNG\r\n\x1a\n",
        _png_chunk(b"IHDR", header),
        _png_chunk(b"IDAT", pixels),
        _png_chunk(b"IEND", b""),
    )


class PngStreamingResponse(StreamingResponse):
    media_type = "image/png"


def create_app() -> FastAPI:
    app = FastAPI()
    png_chunks = _png_chunks()

    @app.get("/telemetry/story/async-typed", response_class=StreamingResponse)
    async def story_async_typed() -> AsyncIterable[str]:
        for chunk in _TEXT_CHUNKS:
            yield chunk

    @app.get("/telemetry/story/sync-typed", response_class=StreamingResponse)
    def story_sync_typed() -> Iterable[str]:
        # Preserve this loop form as an independent sync generator input.
        for chunk in _TEXT_CHUNKS:  # noqa: UP028
            yield chunk

    @app.get("/telemetry/story/async-inferred", response_class=StreamingResponse)
    async def story_async_inferred():
        for chunk in _TEXT_CHUNKS:
            yield chunk

    @app.get("/telemetry/story/sync-inferred", response_class=StreamingResponse)
    def story_sync_inferred():
        yield from _TEXT_CHUNKS

    @app.get("/telemetry/story-bytes/async-typed", response_class=StreamingResponse)
    async def story_bytes_async_typed() -> AsyncIterable[bytes]:
        for chunk in _TEXT_CHUNKS:
            yield chunk.encode("utf-8")

    @app.get("/telemetry/story-bytes/sync-typed", response_class=StreamingResponse)
    def story_bytes_sync_typed() -> Iterable[bytes]:
        for chunk in _TEXT_CHUNKS:
            yield chunk.encode("utf-8")

    @app.get("/telemetry/story-bytes/async-inferred", response_class=StreamingResponse)
    async def story_bytes_async_inferred():
        for chunk in _TEXT_CHUNKS:
            yield chunk.encode("utf-8")

    @app.get("/telemetry/story-bytes/sync-inferred", response_class=StreamingResponse)
    def story_bytes_sync_inferred():
        yield from (chunk.encode("utf-8") for chunk in _TEXT_CHUNKS)

    @app.get("/raster/async-typed", response_class=PngStreamingResponse)
    async def raster_async_typed() -> AsyncIterable[bytes]:
        for chunk in png_chunks:
            yield chunk

    @app.get("/raster/sync-typed", response_class=PngStreamingResponse)
    def raster_sync_typed() -> Iterable[bytes]:
        # Preserve this loop form as an independent sync generator input.
        for chunk in png_chunks:  # noqa: UP028
            yield chunk

    @app.get("/raster/sync-forward", response_class=PngStreamingResponse)
    def raster_sync_forward() -> Iterable[bytes]:
        yield from png_chunks

    @app.get("/raster/async-inferred", response_class=PngStreamingResponse)
    async def raster_async_inferred():
        for chunk in png_chunks:
            yield chunk

    @app.get("/raster/sync-inferred", response_class=PngStreamingResponse)
    def raster_sync_inferred():
        yield from png_chunks

    return app
