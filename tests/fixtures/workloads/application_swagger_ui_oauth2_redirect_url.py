"""Expose FastAPI's documented Swagger OAuth2 redirect field through ASGI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(**factory_input)

    @app.get("/_observe/swagger-ui-oauth2-redirect-url")
    def observe_redirect_url() -> dict[str, str | None]:
        return {"swagger_ui_oauth2_redirect_url": app.swagger_ui_oauth2_redirect_url}

    return app
