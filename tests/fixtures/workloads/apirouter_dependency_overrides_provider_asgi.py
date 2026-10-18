"""Input workload for a dependency override provider on a direct APIRouter."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import APIRouter, Depends, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Mount the configured router in an app to provide FastAPI middleware."""

    def original_dependency() -> str:
        return "original"

    def replacement_dependency() -> str:
        return factory_input["override_value"]

    provider = SimpleNamespace(dependency_overrides={original_dependency: replacement_dependency})
    router = APIRouter(dependency_overrides_provider=provider)

    @router.get("/provider")
    def read_provider_value(value: str = Depends(original_dependency)) -> dict[str, str]:
        return {"value": value}

    app = FastAPI()
    app.mount("/api", router)
    return app
