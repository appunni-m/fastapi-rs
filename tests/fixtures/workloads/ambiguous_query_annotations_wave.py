"""Independent app for query constraints composed from Annotated metadata."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/multi-query")
    async def read_value(foo: Annotated[int, Query(gt=2), Query(lt=10)]) -> int:
        return foo

    return app
