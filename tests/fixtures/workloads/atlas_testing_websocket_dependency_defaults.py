"""Input-only workload for the unoverridden dependency tutorial request."""

from typing import Any

from fastapi import Depends, FastAPI


async def common_parameters(
    q: str | None = None, skip: int = 0, limit: int = 100
) -> dict[str, Any]:
    return {"q": q, "skip": skip, "limit": limit}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(commons: dict[str, Any] = Depends(common_parameters)):  # noqa: B008
        return {"message": "Hello Items!", "params": commons}

    return app
