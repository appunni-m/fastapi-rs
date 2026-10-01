"""Independent construction stimulus for including an APIRouter into itself."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    if factory_input.get("include_router_cycle"):
        parent = APIRouter()
        child = APIRouter()
        parent.include_router(child)
        child.include_router(parent)

    router = APIRouter()
    if factory_input.get("include_router_into_self"):
        router.include_router(router)

    app = FastAPI()
    app.include_router(router)
    return app
