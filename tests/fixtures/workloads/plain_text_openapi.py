"""Input-only workload for response-class media types in OpenAPI."""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


class PlainTextWithoutMediaType(PlainTextResponse):
    media_type = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/plain", response_class=PlainTextResponse)
    async def plain() -> str:
        return "plain"

    @app.get("/plain-without-media-type", response_class=PlainTextWithoutMediaType)
    async def plain_without_media_type() -> str:
        return "plain"

    return app
