"""Independent nested-body validation and Pydantic extra-type serialization."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list = Field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/{item_id}")
    async def replace_item(item_id: int, item: Item) -> dict[str, object]:
        return {"item_id": item_id, "item": item}

    @app.put("/temporal/{item_id}")
    async def process_temporal_item(
        item_id: UUID,
        start_datetime: Annotated[datetime, Body()],
        end_datetime: Annotated[datetime, Body()],
        process_after: Annotated[timedelta, Body()],
        repeat_at: Annotated[time | None, Body()] = None,
    ) -> dict[str, object]:
        start_process = start_datetime + process_after
        duration = end_datetime - start_process
        return {
            "item_id": item_id,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "process_after": process_after,
            "repeat_at": repeat_at,
            "start_process": start_process,
            "duration": duration,
        }

    return app
