"""Independent input for configured OpenAPI tag ordering."""

from __future__ import annotations

from fastapi import FastAPI

_TAGS = [
    {"name": "zebra", "description": "The first configured tag."},
    {"name": "alpha", "description": "The second configured tag."},
]


def create_app() -> FastAPI:
    app = FastAPI(openapi_tags=_TAGS)

    @app.get("/zebra", tags=["zebra"])
    def read_zebra() -> dict[str, str]:
        return {"group": "zebra"}

    @app.get("/alpha", tags=["alpha"])
    def read_alpha() -> dict[str, str]:
        return {"group": "alpha"}

    return app
