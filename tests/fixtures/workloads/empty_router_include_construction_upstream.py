"""Independent construction stimulus for an empty router with no prefix."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()
    app.include_router(APIRouter())
    return app
