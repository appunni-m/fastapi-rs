"""Independent workload for optional parameters inherited as router path fields."""

from collections.abc import Mapping
from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Build the reused-router shape from FastAPI's inferred-parameter test."""
    del factory_input, event_trace
    app = FastAPI()
    item_router = APIRouter()

    @item_router.get("/")
    def get_items(user_id: str | None = None):
        if user_id is None:
            return [
                {"item_id": "i1", "user_id": "u1"},
                {"item_id": "i2", "user_id": "u2"},
            ]
        return [{"item_id": "i2", "user_id": user_id}]

    app.include_router(item_router, prefix="/items")
    app.include_router(item_router, prefix="/users/{user_id}/items")
    return app
