"""Independent custom OpenAPI metadata and cache inputs."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def create_app() -> FastAPI:
    app = FastAPI(title="Initial Interface Probe", version="1.0")

    @app.get("/archives/")
    def read_archives():
        return [{"label": "North Archive"}]

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        document = get_openapi(
            title="Archive Interface Probe",
            version="3.7",
            summary="An independently customized API description",
            description="A custom OpenAPI description for the archive endpoint",
            routes=app.routes,
        )
        document["info"]["x-build-channel"] = "independent-review"
        app.openapi_schema = document
        return app.openapi_schema

    app.openapi = custom_openapi
    return app
