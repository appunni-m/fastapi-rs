"""Independent ASGI inputs for FastAPI's constructor-level OpenAPI tags."""

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    app = FastAPI(openapi_tags=factory_input["tags"])

    @app.get("/users/", tags=["users"])
    async def get_users():
        return [{"name": "Harry"}, {"name": "Ron"}]

    @app.get("/items/", tags=["items"])
    async def get_items():
        return [{"name": "wand"}, {"name": "flying broom"}]

    @app.get("/configured-tags", include_in_schema=False)
    async def configured_tags():
        return app.openapi_tags

    return app
