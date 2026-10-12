"""Input-driven observation of the documented FastAPI.openapi_version field."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(_factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(title="OpenAPI Version Field Probe", version="1.0")
    app.openapi_version = "3.0.2"

    @app.get("/items")
    def read_items():
        return [{"name": "independent item"}]

    return app
