"""Focused Annotated query-bound workflow adapted from FastAPI's tutorial."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items")
    async def read_item(size: Annotated[float, Query(gt=0)]):
        return {"size": size}

    return app
