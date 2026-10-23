"""Input-driven observation of the FastAPI.openapi_schema cache field."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(_factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(title="OpenAPI Schema Field Probe", version="1.0")

    @app.get("/_observe-openapi-schema", include_in_schema=False)
    def observe_openapi_schema() -> dict[str, Any]:
        try:
            app.openapi()
        except AttributeError as exc:
            return {
                "exception_class": type(exc).__name__,
                "exception_message": str(exc),
            }
        return {"schema_present": True}

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
    if _factory_input.get("delete_openapi_schema", False):
        del app.openapi_schema
    return app
