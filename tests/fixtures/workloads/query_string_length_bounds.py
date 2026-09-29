"""Required scalar Query string-length bounds adapted from tutorial 003."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(q: Annotated[str, Query(min_length=3, max_length=50)]):
        return {"q": q}

    return app
