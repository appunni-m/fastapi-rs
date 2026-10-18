"""Input-only APIRouter slash-policy workload."""

from collections.abc import Mapping
from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: Mapping[str, Any], _event_trace: list[str]) -> FastAPI:
    router = APIRouter(**factory_input)

    @router.get("/catalog/")
    async def catalog() -> str:
        return "catalog ready"

    app = FastAPI()
    app.mount("/api", router)
    return app
