"""Input-only async-endpoint workload for a direct coroutine override."""

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    async def common_parameters(
        q: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return {"q": q, "skip": skip, "limit": limit}

    async def overrider_dependency_simple(q: str | None = None):
        return {"q": q, "skip": 5, "limit": 10}

    common_parameters_marker = Depends(common_parameters)

    @app.get("/main-depends/")
    async def main_depends(commons: dict = common_parameters_marker):
        return {"in": "main-depends", "params": commons}

    app.dependency_overrides[common_parameters] = overrider_dependency_simple
    return app
