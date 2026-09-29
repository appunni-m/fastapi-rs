"""Focused Annotated header-name workflow from FastAPI's tutorial."""

from typing import Annotated

from fastapi import FastAPI, Header


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(
        strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
    ):
        return {"strange_header": strange_header}

    return app
