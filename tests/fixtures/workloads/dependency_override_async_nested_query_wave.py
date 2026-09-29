"""Input-only workload for an async override with one async query dependency."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace

    app = FastAPI()

    async def common_parameters(q: str, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return {"q": q, "skip": skip, "limit": limit}

    async def overrider_sub_dependency(k: str) -> dict[str, str]:
        return {"k": k}

    async def overrider_dependency_with_sub(
        msg: dict[str, str] = Depends(overrider_sub_dependency),  # noqa: B008
    ) -> dict[str, str]:
        return msg

    app.dependency_overrides[common_parameters] = overrider_dependency_with_sub

    @app.get("/main-depends/")
    async def main_depends(
        commons: dict[str, Any] = Depends(common_parameters),  # noqa: B008
    ) -> dict[str, Any]:
        return {"in": "main-depends", "params": commons}

    return app
