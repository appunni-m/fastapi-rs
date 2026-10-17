"""Observe public FastAPI application configuration fields through ASGI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(**factory_input)

    @app.get("/_observe/application-attributes")
    def observe_application_attributes() -> dict[str, Any]:
        return {
            "summary": app.summary,
            "description": app.description,
            "version": app.version,
            "terms_of_service": app.terms_of_service,
            "contact": app.contact,
            "license_info": app.license_info,
            "docs_url": app.docs_url,
            "redoc_url": app.redoc_url,
            "swagger_ui_parameters": app.swagger_ui_parameters,
        }

    return app
