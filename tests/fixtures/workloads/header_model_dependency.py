"""Header model extraction inside a callable used through Depends."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header
from pydantic import BaseModel


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


def get_common_headers(headers: Annotated[CommonHeaders, Header()]) -> CommonHeaders:
    return headers


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(
        headers: Annotated[CommonHeaders, Depends(get_common_headers)],
    ) -> CommonHeaders:
        return headers

    return app
