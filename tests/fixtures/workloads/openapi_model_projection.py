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
        "info-all-fields": {
            "args": [],
            "kwargs": {
                "title": "Field Guide",
                "version": "2.4",
                "summary": "Input-defined summary",
                "description": "Input-defined description",
                "termsOfService": "https://example.test/terms",
                "contact": {
                    "name": "API team",
                    "url": "https://example.test/team",
                },
                "license": {
                    "name": "MIT",
                    "identifier": "MIT",
                    "url": "https://opensource.org/license/mit/",
                },
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
        "openapi-components-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Components field", "version": "1.0"},
                "components": {
                    "schemas": {
                        "Pet": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}},
                        }
                    }
                },
            },
        },
        "openapi-external-docs-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "External docs field", "version": "1.0"},
                "externalDocs": {
                    "description": "The full API reference",
                    "url": "https://docs.example.test/reference",
                },
            },
        },
        "openapi-info-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {
                    "title": "Field Guide",
                    "version": "2.4",
                    "summary": "Input-defined metadata",
                    "contact": {
                        "name": "API team",
                        "url": "https://example.test/team",
                    },
                },
            },
        },
        "openapi-json-schema-dialect-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "JSON Schema dialect field", "version": "1.0"},
                "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
            },
        },
        "openapi-version-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "OpenAPI version field", "version": "1.0"},
            },
        },
        "openapi-paths-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Paths field", "version": "1.0"},
                "paths": {
                    "/pets": {
                        "get": {
                            "operationId": "listPets",
                            "responses": {"200": {"description": "A page of pets"}},
                        }
                    }
                },
            },
        },
        "openapi-security-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Security field", "version": "1.0"},
                "security": [{"OAuth2": ["pets:read"]}],
            },
        },
        "openapi-servers-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Servers field", "version": "1.0"},
                "servers": [
                    {
                        "url": "https://api.example.test/v1",
                        "description": "Production API",
                    }
                ],
            },
        },
        "openapi-tags-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Tags field", "version": "1.0"},
                "tags": [
                    {
                        "name": "pets",
                        "description": "Pet operations",
                        "externalDocs": {
                            "description": "Pet documentation",
                            "url": "https://docs.example.test/pets",
                        },
                    }
                ],
            },
        },
        "openapi-webhooks-field": {
            "args": [],
            "kwargs": {
                "openapi": "3.1.0",
                "info": {"title": "Webhooks field", "version": "1.0"},
                "webhooks": {
                    "newSubscription": {
                        "$ref": "#/components/pathItems/newSubscription"
                    }
                },
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
        "example-empty": {"args": [], "kwargs": {}},
        "example-populated-extra": {
            "args": [],
            "kwargs": {
                "summary": "Reference example",
                "description": None,
                "value": {"kind": "pet", "count": 2},
                "externalValue": "not-a-url",
                "x-example-trace": {"source": "fixture"},
            },
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
