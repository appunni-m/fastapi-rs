"""Input-driven routes exposing FastAPI's HTML documentation helpers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/swagger-generated", include_in_schema=False)
    async def swagger_generated():
        return get_swagger_ui_html(openapi_url="/docs", title="title")

    @app.get("/swagger-custom", include_in_schema=False)
    async def swagger_custom():
        return get_swagger_ui_html(
            openapi_url="/docs",
            title="title",
            swagger_js_url="swagger_fake_file.js",
            swagger_css_url="swagger_fake_file.css",
            swagger_favicon_url="swagger_fake_file.png",
        )

    @app.get("/redoc-generated", include_in_schema=False)
    async def redoc_generated():
        return get_redoc_html(openapi_url="/docs", title="title")

    @app.get("/redoc-custom", include_in_schema=False)
    async def redoc_custom():
        return get_redoc_html(
            openapi_url="/docs",
            title="title",
            redoc_js_url="fake_redoc_file.js",
            redoc_favicon_url="fake_redoc_file.png",
        )

    @app.get("/redoc-no-google-fonts", include_in_schema=False)
    async def redoc_without_google_fonts():
        return get_redoc_html(
            openapi_url="/docs",
            title="title",
            with_google_fonts=False,
        )

    return app
