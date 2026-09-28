"""Independent app exercising the public Param default as a query parameter."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.params import Param


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    def read_items(q: str | None = Param(default=None)) -> dict[str, str | None]:
        return {"q": q}

    return app
