"""Observe public FastAPI application configuration fields through ASGI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

_UNSET = object()


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    options = factory_input.copy()
    summary_after_init = options.pop("_summary_after_init", _UNSET)
    app = FastAPI(**options)
    if summary_after_init is not _UNSET:
        app.summary = summary_after_init

    @app.get("/_observe/application-attributes")
    def observe_application_attributes() -> dict[str, Any]:
        return {
            "summary": app.summary,
            "openapi_summary": app.openapi()["info"].get("summary"),
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
