"""Independent streamed byte and JSON Lines ASGI workloads."""

from __future__ import annotations

import struct
import zlib
from collections.abc import AsyncIterable, Iterable

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    size = struct.pack(">I", len(data))
    checksum = struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return size + kind + data + checksum


def _pixel_chunks() -> tuple[bytes, ...]:
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixel = zlib.compress(b"\x00\x21\x43\x65\xff")
    return (
        signature,
        _png_chunk(b"IHDR", header),
        _png_chunk(b"IDAT", pixel),
        _png_chunk(b"IEND", b""),
    )


class PngStream(StreamingResponse):
    media_type = "image/png"


class LineRecord(BaseModel):
    key: str
    count: int
    active: bool


def create_app() -> FastAPI:
    app = FastAPI()
    records = (
        LineRecord(key="north", count=4, active=True),
        LineRecord(key="south", count=9, active=False),
    )

    @app.get("/raster/async-typed", response_class=PngStream)
    async def raster_async_typed() -> AsyncIterable[bytes]:
        for chunk in _pixel_chunks():
            yield chunk

    @app.get("/raster/sync-typed", response_class=PngStream)
    def raster_sync_typed() -> Iterable[bytes]:
        for chunk in _pixel_chunks():  # noqa: UP028 - this case exercises a for-loop generator.
            yield chunk

    @app.get("/raster/sync-forward", response_class=PngStream)
    def raster_sync_forward() -> Iterable[bytes]:
        yield from _pixel_chunks()

    @app.get("/raster/async-inferred", response_class=PngStream)
    async def raster_async_inferred():
        for chunk in _pixel_chunks():
            yield chunk

    @app.get("/raster/sync-inferred", response_class=PngStream)
    def raster_sync_inferred():
        yield from _pixel_chunks()

    @app.get("/lines/async-typed")
    async def lines_async_typed() -> AsyncIterable[LineRecord]:
        for record in records:
            yield record

    @app.get("/lines/sync-typed")
    def lines_sync_typed() -> Iterable[LineRecord]:
        yield from records

    @app.get("/lines/async-inferred")
    async def lines_async_inferred():
        for record in records:
            yield record.model_dump()

    @app.get("/lines/sync-inferred")
    def lines_sync_inferred():
        for record in records:
            yield record.model_dump()

    return app
