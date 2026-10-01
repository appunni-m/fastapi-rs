"""Input-only workload for Pydantic models in additional OpenAPI responses."""

from fastapi import FastAPI
from pydantic import BaseModel


class TeaError(BaseModel):
    message: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/tea",
        responses={418: {"description": "Teapot response", "model": TeaError}},
    )
    async def tea() -> dict[str, str]:
        return {"state": "ready"}

    return app
