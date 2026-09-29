"""Isolated Query-bound workflow adapted from FastAPI tutorial 006."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items")
    async def read_item(size: Annotated[float, Query(gt=0, lt=10.5)]):
        return {"size": size}

    return app
