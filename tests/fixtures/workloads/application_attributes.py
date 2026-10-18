"""Observe public FastAPI application configuration fields through ASGI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

_UNSET = object()


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    options = factory_input.copy()
    summary_after_init = options.pop("_summary_after_init", _UNSET)
    summary_after_openapi = options.pop("_summary_after_openapi", _UNSET)
    contact_after_init = options.pop("_contact_after_init", _UNSET)
    contact_after_openapi = options.pop("_contact_after_openapi", _UNSET)
    delete_contact_after_init = options.pop("_delete_contact_after_init", False)
    openapi_after_contact_deletion = options.pop("_openapi_after_contact_deletion", False)
    delete_contact_after_openapi = options.pop("_delete_contact_after_openapi", False)
    app = FastAPI(**options)
    if summary_after_init is not _UNSET:
        app.summary = summary_after_init
    if contact_after_init is not _UNSET:
        app.contact = contact_after_init

    @app.get("/_observe/application-attributes")
    def observe_application_attributes() -> dict[str, Any]:
        return {
            "summary": app.summary,
            "openapi_summary": app.openapi()["info"].get("summary"),
            "description": app.description,
            "version": app.version,
            "terms_of_service": app.terms_of_service,
            "contact_present": hasattr(app, "contact"),
            "contact": getattr(app, "contact", None),
            "openapi_contact": app.openapi()["info"].get("contact"),
            "license_info": app.license_info,
            "docs_url": app.docs_url,
            "redoc_url": app.redoc_url,
            "swagger_ui_parameters": app.swagger_ui_parameters,
        }

    if summary_after_openapi is not _UNSET:
        app.openapi()
        app.summary = summary_after_openapi
    if delete_contact_after_init:
        delattr(app, "contact")
    if openapi_after_contact_deletion:
        app.openapi()
    if contact_after_openapi is not _UNSET:
        app.openapi()
        app.contact = contact_after_openapi
    if delete_contact_after_openapi:
        app.openapi()
        delattr(app, "contact")

    return app
