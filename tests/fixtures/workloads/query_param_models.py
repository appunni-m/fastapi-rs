"""Independent grouped-query-model workload for the FastAPI ASGI contract."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class ItemFilters(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(filters: Annotated[ItemFilters, Query()]) -> ItemFilters:
        return filters

    return app
