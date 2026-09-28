"""Input workload for effective route context in an included route request."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request


def create_app() -> FastAPI:
    router = APIRouter()

    @router.get("/items")
    def read_items(request: Request):
        fastapi_scope = request.scope.get("fastapi")
        assert isinstance(fastapi_scope, dict)
        return {
            "has_context": "effective_route_context" in fastapi_scope,
            "path": fastapi_scope["effective_route_context"].path,
        }

    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app
