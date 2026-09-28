"""Minimal independent app stimulus for the metadata tutorial item routes."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items():
        return [{"name": "Foo"}]

    return app
