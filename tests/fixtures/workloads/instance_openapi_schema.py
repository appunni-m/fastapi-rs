"""Input-driven observation of the FastAPI.openapi_schema cache field."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(_factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(title="OpenAPI Schema Field Probe", version="1.0")
    app.openapi()
    app.openapi_schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "OpenAPI Schema Field Probe",
            "version": "1.0",
            "x-field-observation": "openapi_schema",
        },
        "paths": {},
    }
    return app
