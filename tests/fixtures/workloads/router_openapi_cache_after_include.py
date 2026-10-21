"""Inputs for checking OpenAPI refresh after a child router gains a route."""

from fastapi import APIRouter, FastAPI


def read_later() -> dict[str, bool]:
    return {"later": True}


def create_app() -> FastAPI:
    router = APIRouter()
    nested_child_router = APIRouter()
    nested_parent_router = APIRouter()
    nested_parent_router.include_router(nested_child_router, prefix="/child")
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.include_router(nested_parent_router, prefix="/api")

    @app.get("/_register-later", include_in_schema=False)
    def register_later() -> dict[str, bool]:
        router.get("/later")(read_later)
        return {"registered": True}

    @app.get("/_register-nested-later", include_in_schema=False)
    def register_nested_later() -> dict[str, bool]:
        first_schema = app.openapi()
        cache_hit_before_route_add = first_schema is app.openapi()
        nested_child_router.get("/later")(read_later)
        refreshed_schema = app.openapi()
        return {
            "cache_hit_before_route_add": cache_hit_before_route_add,
            "route_add_invalidated_cache": refreshed_schema is not first_schema,
            "cache_hit_after_route_add": refreshed_schema is app.openapi(),
            "nested_route_in_schema": "/api/child/later" in refreshed_schema["paths"],
        }

    return app
