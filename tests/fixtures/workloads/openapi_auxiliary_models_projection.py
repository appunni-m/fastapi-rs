"""Input-only constructor bundles for pinned OpenAPI auxiliary models."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "externaldocumentation-defaults": {
            "args": [],
            "kwargs": {"url": "https://example.test/docs"},
        },
        "externaldocumentation-populated": {
            "args": [],
            "kwargs": {
                "description": "External widget documentation",
                "url": "https://example.test/docs/widgets",
                "x-doc-owner": "input-defined",
            },
        },
        "externaldocumentation-invalid-missing-url": {"args": [], "kwargs": {}},
        "license-defaults": {"args": [], "kwargs": {"name": "MIT License"}},
        "license-populated": {
            "args": [],
            "kwargs": {
                "name": "FastAPI-RS",
                "identifier": "MIT",
                "url": "https://example.test/license",
                "x-license-owner": "input-defined",
            },
        },
        "license-invalid-missing-name": {"args": [], "kwargs": {}},
        "tag-defaults": {"args": [], "kwargs": {"name": "widgets"}},
        "tag-populated": {
            "args": [],
            "kwargs": {
                "name": "widgets",
                "description": "Widget operations",
                "externalDocs": {
                    "description": "Widget API reference",
                    "url": "https://example.test/docs/widgets",
                },
                "x-tag-owner": "input-defined",
            },
        },
        "tag-invalid-name": {"args": [], "kwargs": {"name": []}},
        "xml-defaults": {"args": [], "kwargs": {}},
        "xml-populated": {
            "args": [],
            "kwargs": {
                "name": "widget",
                "namespace": "urn:widgets",
                "prefix": "w",
                "attribute": True,
                "wrapped": False,
                "x-xml-owner": "input-defined",
            },
        },
        "xml-invalid-wrapped": {
            "args": [],
            "kwargs": {"wrapped": "sometimes"},
        },
    }
