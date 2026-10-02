"""Independent argument bundles for direct FastAPI get_openapi API probes."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Return deterministic public-call inputs; expected outputs live only in results."""
    return {
        "empty-routes": {
            "args": [],
            "kwargs": {
                "title": "Direct OpenAPI API Probe",
                "version": "1.0.0",
                "routes": [],
            },
        },
        "document-metadata": {
            "args": [],
            "kwargs": {
                "title": "Metadata OpenAPI Probe",
                "version": "2.4.1",
                "summary": "A direct metadata probe",
                "description": "A deterministic description.",
                "routes": [],
                "tags": [{"name": "items", "description": "Item operations"}],
                "servers": [{"url": "https://api.example.invalid"}],
                "terms_of_service": "https://example.invalid/terms",
                "contact": {"name": "Support", "email": "api@example.invalid"},
                "license_info": {"name": "MIT", "identifier": "MIT"},
                "external_docs": {
                    "description": "API guide",
                    "url": "https://docs.example.invalid",
                },
            },
        },
    }
