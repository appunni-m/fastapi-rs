"""Independent ASGI stimuli for custom docs and static UI asset guide sections."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles


def _add_custom_docs(
    app: FastAPI,
    *,
    swagger_js_url: str,
    swagger_css_url: str,
    redoc_js_url: str,
) -> None:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> Any:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect() -> Any:
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html() -> Any:
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url=redoc_js_url,
        )


def _add_api_route(app: FastAPI) -> None:
    @app.get("/users/{username}")
    async def read_user(username: str) -> dict[str, str]:
        return {"message": f"Hello {username}"}


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one documented app scenario per input case."""
    del event_trace
    scenario = factory_input["scenario"]

    if scenario == "automatic-docs-disabled":
        app = FastAPI(docs_url=None, redoc_url=None)
        _add_api_route(app)
        return app

    if scenario == "custom-cdn":
        app = FastAPI(docs_url=None, redoc_url=None)
        _add_custom_docs(
            app,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        )
        _add_api_route(app)
        return app

    if scenario == "custom-self-hosted":
        app = FastAPI(docs_url=None, redoc_url=None)
        temporary_directory = tempfile.TemporaryDirectory(prefix="fastapi-rs-docs-ui-assets-")
        static_directory = Path(temporary_directory.name)
        for file_name, file_content in factory_input["static_files"].items():
            (static_directory / file_name).write_text(file_content, encoding="utf-8")
        app.mount(
            "/static",
            StaticFiles(directory=static_directory),
            name="static",
        )
        app.state.source_review_temporary_directory = temporary_directory
        _add_custom_docs(
            app,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            redoc_js_url="/static/redoc.standalone.js",
        )
        _add_api_route(app)
        return app

    raise ValueError(f"unknown UI/client documentation scenario: {scenario}")
