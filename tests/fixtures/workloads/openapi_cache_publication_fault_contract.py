"""Route workload for the target-only OpenAPI cache publication fault contract."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI(title="OpenAPI cache publication recovery")

    @app.get("/items/{item_id}")
    async def read_item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    return app
