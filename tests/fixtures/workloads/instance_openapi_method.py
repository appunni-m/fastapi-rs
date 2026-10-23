"""Observe a per-instance FastAPI.openapi replacement through ASGI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(title="OpenAPI Method Replacement Probe", version="1.0")
    document = factory_input["document"]

    def replacement_openapi() -> dict[str, Any]:
        return document

    app.openapi = replacement_openapi
    return app
