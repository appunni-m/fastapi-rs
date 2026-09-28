"""Input-only workload for dependency-override tutorial HTTP cases."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI


async def common_parameters(
    q: str | None = None, skip: int = 0, limit: int = 100
) -> dict[str, Any]:
    return {"q": q, "skip": skip, "limit": limit}


async def override_dependency(q: str | None = None) -> dict[str, Any]:
    return {"q": q, "skip": 5, "limit": 10}


def create_app() -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[common_parameters] = override_dependency

    @app.get("/items/")
    async def read_items(commons: dict[str, Any] = Depends(common_parameters)):  # noqa: B008
        return {"message": "Hello Items!", "params": commons}

    @app.get("/users/")
    async def read_users(commons: dict[str, Any] = Depends(common_parameters)):  # noqa: B008
        return {"message": "Hello Users!", "params": commons}

    @app.get("/annotated/items/")
    async def read_annotated_items(
        commons: Annotated[dict[str, Any], Depends(common_parameters)],
    ):
        return {"message": "Hello Items!", "params": commons}

    @app.get("/annotated/users/")
    async def read_annotated_users(
        commons: Annotated[dict[str, Any], Depends(common_parameters)],
    ):
        return {"message": "Hello Users!", "params": commons}

    return app
