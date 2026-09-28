"""Independent optional/required query forms over integer path parameters."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Path, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/optional/items/{item_id}")
    async def optional_query_item(
        item_id: int = Path(title="The ID of the item to get"),
        q: str | None = Query(default=None, alias="item-query"),
    ) -> dict[str, Any]:
        result: dict[str, Any] = {"item_id": item_id}
        if q:
            result["q"] = q
        return result

    @app.get("/required/items/{item_id}")
    async def required_query_item(
        q: str,
        item_id: int = Path(title="The ID of the item to get"),
    ) -> dict[str, Any]:
        result: dict[str, Any] = {"item_id": item_id}
        if q:
            result["q"] = q
        return result

    return app
