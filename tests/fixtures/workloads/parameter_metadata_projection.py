"""Public FastAPI parameter factory arguments for metadata observations."""

from __future__ import annotations

from pydantic.aliases import AliasChoices


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "path-alias-constraint": {
            "args": [],
            "kwargs": {"alias": "item-id", "gt": 0},
        },
        "query-alias-default": {
            "args": [],
            "kwargs": {
                "default": None,
                "alias": "external-id",
                "validation_alias": AliasChoices("legacy-id", "external-id"),
                "serialization_alias": "wire-id",
                "alias_priority": 2,
            },
        },
        "query-default-factory": {
            "args": [],
            "kwargs": {"default_factory": list},
        },
        "query-constraints-examples": {
            "args": [],
            "kwargs": {
                "gt": 1,
                "max_length": 8,
                "examples": ["sample"],
                "example": "legacy",
                "openapi_examples": {"sample": {"summary": "Sample value", "value": "sample"}},
                "deprecated": True,
            },
        },
        "header-alias": {
            "args": ["guest"],
            "kwargs": {"alias": "X-Client-ID", "convert_underscores": False},
        },
        "cookie-alias-default": {
            "args": ["guest"],
            "kwargs": {"alias": "session-id"},
        },
        "body-media-embed": {
            "args": [{"name": "Ada"}],
            "kwargs": {"embed": True, "media_type": "application/vnd.example+json"},
        },
        "form-media-embed": {
            "args": ["guest"],
            "kwargs": {"embed": True, "media_type": "application/x-www-form-urlencoded"},
        },
        "file-media-embed": {
            "args": [],
            "kwargs": {"embed": True, "media_type": "application/octet-stream"},
        },
    }
