"""Minimal app workload for application-level OpenAPI metadata."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(
        title="Metadata API",
        summary="A concise API summary.",
        description="Markdown **description** for the API.",
        terms_of_service="https://example.test/terms",
        contact={
            "name": "API Support",
            "url": "https://example.test/contact",
            "email": "support@example.test",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_external_docs={
            "description": "External API documentation.",
            "url": "https://docs.example.com/api-general",
        },
    )
