"""Inputs for checking OpenAPI cache identity and route/root-path behavior."""

from fastapi import FastAPI


def late_route() -> dict[str, str]:
    return {"state": "late"}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/ready")
    def ready() -> dict[str, bool]:
        return {"ready": True}

    @app.get("/activate-late-route", include_in_schema=False)
    def activate_late_route() -> dict[str, bool]:
        first_schema = app.openapi()
        cache_hit = first_schema is app.openapi()
        app.add_api_route("/late", late_route)
        refreshed_schema = app.openapi()
        return {
            "cache_hit_before_route_add": cache_hit,
            "route_add_invalidated_cache": refreshed_schema is not first_schema,
            "cache_hit_after_route_add": refreshed_schema is app.openapi(),
            "late_route_in_schema": "/late" in refreshed_schema["paths"],
        }

    return app
