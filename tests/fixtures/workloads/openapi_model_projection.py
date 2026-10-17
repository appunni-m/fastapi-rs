"""Input-only constructor bundles for direct OpenAPI Pydantic model projection."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
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
        "info": {
            "args": [],
            "kwargs": {
                "title": "Field Guide",
                "version": "2.4",
                "summary": "Input-defined metadata",
                "contact": {"name": "API team", "url": "https://example.test/team"},
                "x-document-owner": "compatibility",
            },
        },
        "openapi": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Field Guide", "version": "2.4"},
                "paths": {},
                "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
                "x-document-owner": "compatibility",
            },
        },
        "reference": {
            "args": [],
            "kwargs": {
                "$ref": "#/components/schemas/FieldGuide",
                "x-source": "input-defined",
            },
        },
        "reference-field-name-only": {
            "args": [],
            "kwargs": {"ref": "#/components/schemas/FieldGuide"},
        },
        "encoding": {
            "args": [],
            "kwargs": {
                "contentType": "application/json",
                "headers": {
                    "Trace-Id": {
                        "description": "Request tracing identifier",
                        "required": True,
                        "x-header-source": "input-defined",
                    },
                    "Common": {"$ref": "#/components/headers/Common"},
                },
                "style": "form",
                "explode": True,
                "allowReserved": False,
                "x-encoding-source": "input-defined",
            },
        },
        "encoding-defaults": {"args": [], "kwargs": {}},
        "encoding-invalid-explode": {
            "args": [],
            "kwargs": {"explode": "sometimes"},
        },
        "media-type": {
            "args": [],
            "kwargs": {
                "schema": {
                    "type": "string",
                    "title": "Media type schema",
                    "x-schema-source": "input-defined",
                },
                "example": {"kind": "pet", "name": "Momo"},
                "examples": {
                    "pet": {
                        "summary": "Example pet",
                        "value": {"kind": "pet", "name": "Momo"},
                        "x-example-source": "input-defined",
                    },
                    "shared": {"$ref": "#/components/examples/shared"},
                },
                "encoding": {
                    "application/json": {
                        "contentType": "application/json",
                        "headers": {
                            "Trace-Id": {
                                "description": "Request tracing identifier",
                                "required": True,
                            },
                            "Common": {"$ref": "#/components/headers/Common"},
                        },
                        "style": "form",
                        "explode": True,
                        "allowReserved": False,
                    }
                },
                "x-media-type-source": "input-defined",
            },
        },
        "media-type-defaults": {"args": [], "kwargs": {}},
        "media-type-invalid-schema": {
            "args": [],
            "kwargs": {"schema": 1},
        },
        "contact": {
            "args": [],
            "kwargs": {
                "name": "Field Guide team",
                "url": "https://example.test/contact",
                "email": "api@example.com",
                "x-contact-source": "input-defined",
            },
        },
        "contact-defaults": {"args": [], "kwargs": {}},
        "contact-invalid-email": {
            "args": [],
            "kwargs": {"email": "not-an-email"},
        },
        "openapi-missing-info": {
            "args": [],
            "kwargs": {"openapi": "3.1.0", "paths": {}},
        },
    }
