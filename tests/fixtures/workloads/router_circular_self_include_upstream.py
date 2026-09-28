"""Independent construction stimulus for including an APIRouter into itself."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    router = APIRouter()
    if factory_input["include_router_into_self"]:
        router.include_router(router)

    app = FastAPI()
    app.include_router(router)
    return app
