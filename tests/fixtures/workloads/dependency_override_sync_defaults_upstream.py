"""Input-only workload for sync dependency override defaults."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    def original(q: str | None = None, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return {"q": q, "skip": skip, "limit": limit}

    def replacement(q: str | None = None) -> dict[str, Any]:
        return {"q": q, "skip": 5, "limit": 10}

    @app.get("/items/")
    def read_items(params: dict[str, Any] = Depends(original)) -> dict[str, Any]:  # noqa: B008
        return {"message": "Hello Items!", "params": params}

    app.dependency_overrides[original] = replacement
    return app
