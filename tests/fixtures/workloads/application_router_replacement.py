"""Exercise a route registered through an app's replaced router."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        redirect_slashes=False,
        strict_content_type=False,
    )
    app.router = APIRouter(prefix="/replacement")

    @app.router.get("/probe", response_model=None)
    def replacement_probe() -> dict[str, str]:
        return {"router": "replacement"}

    return app
