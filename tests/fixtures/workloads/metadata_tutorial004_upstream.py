"""App for the metadata tutorial's external tag documentation case."""

from __future__ import annotations

from fastapi import FastAPI

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


def create_app() -> FastAPI:
    app = FastAPI(openapi_tags=tags_metadata)

    @app.get("/users/", tags=["users"])
    async def get_users() -> list[dict[str, str]]:
        return [{"name": "Harry"}, {"name": "Ron"}]

    @app.get("/items/", tags=["items"])
    async def get_items() -> list[dict[str, str]]:
        return [{"name": "wand"}, {"name": "flying broom"}]

    return app
