"""Independent ASGI stimuli for Starlette response classes and streaming."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

import anyio
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from pydantic import BaseModel

_FILE_RESPONSE_MTIME = 1_700_000_000
_FILE_RESPONSE_BYTES = b"original-file-content"
_FILE_RESPONSE_MUTATED_PATH_BYTES = b"mutated-path-content"


def _write_file_response_input(path: Path, contents: bytes) -> None:
    path.write_bytes(contents)
    os.utime(path, (_FILE_RESPONSE_MTIME, _FILE_RESPONSE_MTIME))


class Item(BaseModel):
    title: str
    timestamp: str
    description: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(default_response_class=HTMLResponse)
    file_response_directory = tempfile.TemporaryDirectory(
        prefix="fastapi-rs-file-response-call-time-"
    )
    file_response_root = Path(file_response_directory.name)
    file_response_original = file_response_root / "original.txt"
    file_response_mutated = file_response_root / "mutated.txt"
    _write_file_response_input(file_response_original, _FILE_RESPONSE_BYTES)
    _write_file_response_input(file_response_mutated, _FILE_RESPONSE_MUTATED_PATH_BYTES)
    app.state.file_response_directory = file_response_directory

    @app.get("/plain", response_class=PlainTextResponse)
    async def plain_text():
        return "Hello World"

    @app.get("/redirect", response_class=JSONResponse)
    async def redirect():
        return RedirectResponse("https://example.test/destination")

    @app.get("/stream")
    async def stream_chunks():
        async def generate():
            for _ in range(10):
                yield b"stream-part;"
                await anyio.sleep(0)

        return StreamingResponse(generate(), media_type="application/octet-stream")

    @app.get("/stream-file")
    def stream_file():
        def iter_file():
            with Path(__file__).open("rb") as file_like:
                yield from file_like

        return StreamingResponse(iter_file(), media_type="video/mp4")

    @app.get("/file")
    async def file_response():
        return FileResponse(Path(__file__))

    @app.get("/file-inline")
    async def inline_file_response():
        return FileResponse(
            file_response_original,
            filename="preview.txt",
            content_disposition_type="inline",
        )

    @app.get("/file-class", response_class=FileResponse)
    async def file_response_class():
        return str(Path(__file__))

    @app.get("/file-call-time/status-code")
    async def file_response_mutated_status_code():
        response = FileResponse(file_response_original, status_code=200)
        response.status_code = 201
        return response

    @app.get("/file-call-time/path")
    async def file_response_mutated_path():
        response = FileResponse(file_response_original)
        response.path = file_response_mutated
        return response

    @app.get("/file-call-time/stat-result")
    async def file_response_mutated_stat_result():
        response = FileResponse(file_response_original)
        response.stat_result = os.stat_result(
            (
                stat.S_IFREG | 0o644,
                1,
                1,
                1,
                0,
                0,
                4,
                _FILE_RESPONSE_MTIME,
                _FILE_RESPONSE_MTIME + 5,
                _FILE_RESPONSE_MTIME + 5,
            )
        )
        return response

    @app.get("/items/", response_class=HTMLResponse)
    async def html_items():
        return "<h1>Items</h1><p>Response class selection.</p>"

    @app.put("/items/{item_id}")
    def update_item(item_id: str, item: Item):
        return JSONResponse(content=jsonable_encoder(item))

    @app.get("/headers/")
    def headers_response():
        return JSONResponse(
            content={"message": "headers"},
            headers={"X-Response-Probe": "present", "Content-Language": "en-US"},
        )

    @app.post("/cookie/")
    def cookie_response():
        response = JSONResponse({"message": "cookie"})
        response.set_cookie(key="session", value="sample-session")
        return response

    return app
