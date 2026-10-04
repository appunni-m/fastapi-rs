"""Input-only constructor bundles for direct OpenAPI Pydantic model projection."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "schema": {
            "args": [],
            "kwargs": {
                "schema_": "https://json-schema.org/draft/2020-12/schema",
                "id": "https://schemas.example.test/pet",
                "title": "Pet",
                "type": "object",
                "required": ["kind", "name"],
                "properties": {
                    "kind": {"type": "string"},
                    "name": {"type": "string", "minLength": 1},
                },
                "additionalProperties": False,
                "discriminator": {
                    "propertyName": "kind",
                    "mapping": {
                        "cat": "#/components/schemas/Cat",
                        "dog": "#/components/schemas/Dog",
                    },
                },
                "x-display-name": "pet schema",
            },
        },
        "discriminator": {
            "args": [],
            "kwargs": {
                "propertyName": "kind",
                "mapping": {
                    "cat": "#/components/schemas/Cat",
                    "dog": "#/components/schemas/Dog",
                },
            },
        },
        "components": {
            "args": [],
            "kwargs": {
                "schemas": {
                    "Pet": {
                        "title": "Pet",
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                    "PetReference": {"$ref": "#/components/schemas/Pet"},
                },
                "x-registry": {"owner": "fastapi-rs", "revision": 1},
            },
        },
        "api-key": {
            "args": [],
            "kwargs": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "A project key",
                "x-owner": "input-defined",
            },
        },
    }
