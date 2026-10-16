"""Expose the documented FastAPI OpenAPI URL field through an ASGI route."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(**factory_input)

    @app.get("/_observe/openapi-url")
    def observe_openapi_url() -> dict[str, str | None]:
        return {"openapi_url": app.openapi_url}

    return app
