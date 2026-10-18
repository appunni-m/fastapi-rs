"""Query-model parameters resolved inside a FastAPI dependency callable."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, Field


class ItemFilters(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    tags: list[str] = Field(default_factory=list)


def get_filters(filters: Annotated[ItemFilters, Query()]) -> ItemFilters:
    return filters


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(
        filters: Annotated[ItemFilters, Depends(get_filters)],
    ) -> ItemFilters:
        return filters

    return app
