"""Independent workflow for automatic and explicit successful status codes."""

from __future__ import annotations

from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    records: dict[str, dict[str, str | int | None]] = {
        "aurora": {"name": "Waypoint", "size": 5},
    }
    app = FastAPI()

    @app.put("/items/{item_id}")
    async def save_item(
        item_id: str,
        name: str | None = Body(default=None),
        size: int | None = Body(default=None),
    ):
        if item_id in records:
            record = records[item_id]
            record.update({"name": name, "size": size})
            return record
        record = {"name": name, "size": size}
        records[item_id] = record
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=record)

    return app
