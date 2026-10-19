"""Input-only constructor bundles for direct OpenAPI model projection."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "header-defaults": {"args": [], "kwargs": {}},
        "header-populated": {
            "args": [],
            "kwargs": {
                "description": "Request tracing identifier",
                "required": False,
                "deprecated": False,
                "style": "simple",
                "explode": False,
                "allowReserved": False,
                "schema": {
                    "type": "string",
                    "minLength": 1,
                    "x-schema-source": "input-defined",
                },
                "example": "trace-42",
                "examples": {
                    "trace": {
                        "summary": "Trace identifier",
                        "value": "trace-42",
                        "x-example-source": "input-defined",
                    },
                    "shared": {"$ref": "#/components/examples/shared-trace"},
                },
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"trace": {"type": "string"}},
                            "x-nested-schema": "input-defined",
                        },
                        "example": {"trace": "trace-42"},
                        "examples": {
                            "trace": {
                                "summary": "Trace payload",
                                "value": {"trace": "trace-42"},
                                "x-nested-example": True,
                            },
                            "shared": {"$ref": "#/components/examples/shared-payload"},
                        },
                        "encoding": {
                            "trace": {
                                "contentType": "text/plain",
                                "headers": {
                                    "X-Format": {
                                        "description": "Trace format",
                                        "x-nested-header": "input-defined",
                                    },
                                    "Common": {"$ref": "#/components/headers/Common"},
                                },
                                "style": "form",
                                "explode": True,
                                "allowReserved": False,
                                "x-nested-encoding": "input-defined",
                            }
                        },
                        "x-nested-media-type": "input-defined",
                    }
                },
                "x-header-extra": {"owner": "fixture"},
            },
        },
        "parameter-base-defaults": {"args": [], "kwargs": {}},
        "parameter-base-populated": {
            "args": [],
            "kwargs": {
                "description": "A cursor parameter",
                "required": True,
                "deprecated": True,
                "style": "form",
                "explode": True,
                "allowReserved": True,
                "schema": {"$ref": "#/components/schemas/Cursor"},
                "example": {"after": "cursor-9"},
                "examples": {
                    "cursor": {
                        "summary": "Cursor example",
                        "value": {"after": "cursor-9"},
                    },
                    "shared": {"$ref": "#/components/examples/shared-cursor"},
                },
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Cursor"},
                        "example": {"after": "cursor-9"},
                        "x-media-type-extra": "input-defined",
                    }
                },
                "x-parameter-base-extra": ["kept", "as", "input"],
            },
        },
        "parameter-defaults": {
            "args": [],
            "kwargs": {"name": "page", "in": "query"},
        },
        "parameter-populated": {
            "args": [],
            "kwargs": {
                "name": "labels",
                "in": "query",
                "description": "Filter by one or more labels",
                "required": False,
                "deprecated": False,
                "style": "form",
                "explode": True,
                "allowReserved": False,
                "schema": {
                    "type": "array",
                    "items": {"type": "string", "x-item-extra": "input-defined"},
                    "minItems": 1,
                    "x-schema-extra": "input-defined",
                },
                "example": ["systems", "api"],
                "examples": {
                    "two-labels": {
                        "summary": "Two labels",
                        "value": ["systems", "api"],
                        "x-example-extra": "input-defined",
                    },
                    "shared": {"$ref": "#/components/examples/label-list"},
                },
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "examples": {"one": {"summary": "One label", "value": ["systems"]}},
                        "x-media-type-extra": "input-defined",
                    }
                },
                "x-parameter-extra": {"reviewed": True},
            },
        },
        "request-body-defaults": {"args": [], "kwargs": {"content": {}}},
        "request-body-populated": {
            "args": [],
            "kwargs": {
                "description": "A nested JSON request body",
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {"name": {"type": "string", "minLength": 1}},
                            "x-request-schema": "input-defined",
                        },
                        "example": {"name": "Widget"},
                        "examples": {
                            "widget": {
                                "summary": "Widget request",
                                "value": {"name": "Widget"},
                                "x-request-example": "input-defined",
                            },
                            "shared": {"$ref": "#/components/examples/widget-request"},
                        },
                        "encoding": {
                            "name": {
                                "contentType": "text/plain",
                                "headers": {
                                    "X-Name-Source": {
                                        "description": "Name source",
                                        "x-encoding-header": "input-defined",
                                    }
                                },
                                "style": "form",
                                "explode": False,
                                "allowReserved": False,
                            }
                        },
                        "x-request-media-type": "input-defined",
                    },
                    "application/vnd.example.widget+json": {
                        "schema": {"$ref": "#/components/schemas/Widget"}
                    },
                },
                "x-request-body-extra": "input-defined",
            },
        },
        "response-defaults": {"args": [], "kwargs": {"description": "No content"}},
        "response-populated": {
            "args": [],
            "kwargs": {
                "description": "A populated response",
                "headers": {
                    "X-Trace": {
                        "description": "Request trace identifier",
                        "required": False,
                        "schema": {"type": "string", "x-response-header-schema": True},
                        "example": "trace-42",
                        "x-response-header-extra": "input-defined",
                    },
                    "Common": {"$ref": "#/components/headers/Common"},
                },
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}},
                            "x-response-schema": "input-defined",
                        },
                        "example": {"id": 42},
                        "examples": {
                            "item": {"summary": "One item", "value": {"id": 42}},
                            "shared": {"$ref": "#/components/examples/item"},
                        },
                        "x-response-media-type": "input-defined",
                    }
                },
                "links": {
                    "NextPage": {
                        "operationId": "listItems",
                        "operationRef": "#/paths/~1items/get",
                        "parameters": {"cursor": "next-cursor"},
                        "requestBody": {"include": ["summary"]},
                        "description": "Follow the next page link",
                        "server": {
                            "url": "https://api.example.test/v1/{tenant}",
                            "description": "Tenant server",
                            "variables": {
                                "tenant": {
                                    "default": "acme",
                                    "enum": ["acme", "globex"],
                                    "description": "Tenant identifier",
                                    "x-server-variable": "input-defined",
                                }
                            },
                            "x-server-extra": "input-defined",
                        },
                        "x-response-link-extra": "input-defined",
                    },
                    "Shared": {"$ref": "#/components/links/Shared"},
                },
                "x-response-extra": {"source": "fixture"},
            },
        },
        "link-defaults": {"args": [], "kwargs": {}},
        "link-populated": {
            "args": [],
            "kwargs": {
                "operationRef": "#/paths/~1items~1{item_id}/get",
                "operationId": "getItem",
                "parameters": {"item_id": "item-42", "expand": ["owner", "labels"]},
                "requestBody": {"include": ["owner", "labels"]},
                "description": "Retrieve the item with related data",
                "server": {
                    "url": "https://api.example.test/v2/{region}",
                    "description": "Regional server",
                    "variables": {
                        "region": {
                            "default": "us-east",
                            "enum": ["us-east", "eu-west"],
                            "description": "Deployment region",
                        }
                    },
                    "x-link-server-extra": "input-defined",
                },
                "x-link-extra": {"owner": "fixture"},
            },
        },
        "parameter-missing-required-fields": {"args": [], "kwargs": {}},
        "parameter-invalid-in": {"args": [], "kwargs": {"name": "payload", "in": "body"}},
        "parameter-python-field-name-in": {
            "args": [],
            "kwargs": {"name": "cursor", "in_": "query"},
        },
        "parameter-base-python-field-name-schema": {
            "args": [],
            "kwargs": {"schema_": {"type": "string", "x-schema-extra": "input-defined"}},
        },
        "request-body-missing-content": {"args": [], "kwargs": {}},
        "response-missing-description": {"args": [], "kwargs": {}},
    }
