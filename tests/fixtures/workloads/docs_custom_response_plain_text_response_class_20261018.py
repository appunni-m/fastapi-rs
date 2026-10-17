"""Input-only FastAPI route for response_class PlainTextResponse behavior."""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/plain", response_class=PlainTextResponse)
    async def plain_text() -> str:
        return "independent plain text"

    return app
