"""Query metadata ordering and unrelated Annotated metadata through FastAPI."""

from typing import Annotated

from fastapi import APIRouter, FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/default")
    async def default(foo: Annotated[str, Query()] = "foo") -> dict[str, str]:
        return {"foo": foo}

    @app.get("/required")
    async def required(foo: Annotated[str, Query(min_length=1)]) -> dict[str, str]:
        return {"foo": foo}

    @app.get("/multiple")
    async def multiple(foo: Annotated[str, object(), Query(min_length=1)]) -> dict[str, str]:
        return {"foo": foo}

    @app.get("/unrelated")
    async def unrelated(foo: Annotated[str, object()]) -> dict[str, str]:
        return {"foo": foo}

    @app.get("/test1")
    @app.get("/test2")
    async def multi_path(var: Annotated[str, Query()] = "bar") -> dict[str, str]:
        return {"foo": var}

    router = APIRouter(prefix="/nested")

    @router.get("/test")
    async def nested(var: Annotated[str, Query()] = "bar") -> dict[str, str]:
        return {"foo": var}

    app.include_router(router)
    return app
