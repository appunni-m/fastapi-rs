"""Input-only workload for an async override with two required query inputs."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI


def create_app(
    factory_input: dict[str, Any] | None = None,
    event_trace: list[str] | None = None,
) -> FastAPI:
    del factory_input, event_trace

    app = FastAPI()

    def original_dependency() -> dict[str, str]:
        return {"source": "original"}

    async def required_query_dependency(k: str, revision: int) -> dict[str, Any]:
        return {"k": k, "revision": revision}

    async def replacement_dependency(
        values: dict[str, Any] = Depends(required_query_dependency),  # noqa: B008
    ) -> dict[str, Any]:
        return values

    app.dependency_overrides[original_dependency] = replacement_dependency

    @app.get("/main-depends/")
    async def main_depends(
        values: dict[str, Any] = Depends(original_dependency),  # noqa: B008
    ) -> dict[str, Any]:
        return {"in": "main-depends", "params": values}

    return app
