"""Independent public-route inputs for a required nested override dependency."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace

    app = FastAPI()

    def original_parameters(q: str, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return {"q": q, "skip": skip, "limit": limit}

    def replacement_subdependency(k: str) -> dict[str, str]:
        return {"k": k}

    def replacement_dependency(
        msg: dict[str, str] = Depends(replacement_subdependency),  # noqa: B008
    ) -> dict[str, str]:
        return msg

    app.dependency_overrides[original_parameters] = replacement_dependency

    @app.get("/main-depends/")
    def read_main_dependency(
        parameters: dict[str, str] = Depends(original_parameters),  # noqa: B008
    ) -> dict[str, Any]:
        return {"in": "main-depends", "params": parameters}

    return app
