"""Observe FastAPI's public router object and its initial route state."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        redirect_slashes=False,
        strict_content_type=False,
    )

    @app.get("/items")
    def list_items() -> dict[str, list[str]]:
        return {"items": ["one"]}

    @app.router.get("/router-items")
    def list_router_items() -> dict[str, list[str]]:
        return {"items": ["two"]}

    @app.get("/_observe/router")
    def observe_router() -> dict[str, object]:
        router = app.router
        return {
            "same_instance": router is app.router,
            "prefix": router.prefix,
            "redirect_slashes": router.redirect_slashes,
            "strict_content_type": router.strict_content_type,
            "default_response_class": router.default_response_class.value.__name__,
            "dependencies": router.dependencies,
            "router_paths": [route.path for route in router.routes],
            "app_paths": [route.path for route in app.routes],
        }

    return app
