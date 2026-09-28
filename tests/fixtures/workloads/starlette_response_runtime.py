"""Independent ASGI stimuli for Starlette response classes and streaming."""

from __future__ import annotations

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


class Item(BaseModel):
    title: str
    timestamp: str
    description: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(default_response_class=HTMLResponse)

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

    @app.get("/file-class", response_class=FileResponse)
    async def file_response_class():
        return str(Path(__file__))

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
