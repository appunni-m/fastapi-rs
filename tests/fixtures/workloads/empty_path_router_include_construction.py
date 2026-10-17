"""Construction input for the empty-path, empty-prefix router include error."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()
    router = APIRouter()

    @router.get("")
    async def get_empty():
        return ["OK"]

    if factory_input["inclusion_api"] == "apirouter":
        parent_router = APIRouter()
        parent_router.include_router(router)
    else:
        app.include_router(router)
    return app
