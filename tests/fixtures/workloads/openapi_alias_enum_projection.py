"""Input-only direct constructor bundles for OpenAPI aliases, unions, and enums."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "schema-type-array": {"args": [], "kwargs": {"type": "array"}},
        "schema-type-boolean": {"args": [], "kwargs": {"type": "boolean"}},
        "schema-type-integer": {"args": [], "kwargs": {"type": "integer"}},
        "schema-type-null": {"args": [], "kwargs": {"type": "null"}},
        "schema-type-number": {"args": [], "kwargs": {"type": "number"}},
        "schema-type-object": {"args": [], "kwargs": {"type": "object"}},
        "schema-type-string": {"args": [], "kwargs": {"type": "string"}},
        "schema-type-list": {
            "args": [],
            "kwargs": {
                "type": [
                    "array",
                    "boolean",
                    "integer",
                    "null",
                    "number",
                    "object",
                    "string",
                ]
            },
        },
        "schema-type-invalid": {"args": [], "kwargs": {"type": "not-a-json-schema-type"}},
        "schema-or-bool-recursive": {
            "args": [],
            "kwargs": {
                "$defs": {
                    "always": True,
                    "never": False,
                    "object": {
                        "type": "object",
                        "properties": {"enabled": {"type": "boolean"}},
                    },
                },
                "allOf": [True, {"type": ["string", "null"]}],
                "anyOf": [False, {"type": "number"}],
                "oneOf": [{"type": "integer"}, True],
                "not": False,
                "if": {"type": "array"},
                "then": {"type": "string"},
                "else": True,
                "items": False,
                "contains": {"type": "string"},
                "properties": {"enabled": True, "count": {"type": "integer"}},
                "additionalProperties": False,
                "contentSchema": {"type": "string"},
            },
        },
        "schema-or-bool-invalid": {
            "args": [],
            "kwargs": {"properties": {"broken": ["not", "a", "schema"]}},
        },
        "parameter-in-query": {
            "args": [],
            "kwargs": {"name": "filter", "in": "query"},
        },
        "parameter-in-header": {
            "args": [],
            "kwargs": {"name": "X-Trace", "in": "header"},
        },
        "parameter-in-path": {
            "args": [],
            "kwargs": {"name": "item_id", "in": "path"},
        },
        "parameter-in-cookie": {
            "args": [],
            "kwargs": {"name": "session", "in": "cookie"},
        },
        "parameter-in-python-name": {
            "args": [],
            "kwargs": {"name": "filter", "in_": "query"},
        },
        "parameter-in-invalid": {
            "args": [],
            "kwargs": {"name": "filter", "in": "body"},
        },
        "api-key-in-query": {
            "args": [],
            "kwargs": {"type": "apiKey", "in": "query", "name": "X-API-Key"},
        },
        "api-key-in-header": {
            "args": [],
            "kwargs": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        },
        "api-key-in-cookie": {
            "args": [],
            "kwargs": {"type": "apiKey", "in": "cookie", "name": "session_key"},
        },
        "api-key-in-invalid": {
            "args": [],
            "kwargs": {"type": "apiKey", "in": "body", "name": "X-API-Key"},
        },
        "components-security-schemes": {
            "args": [],
            "kwargs": {
                "securitySchemes": {
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                    },
                    "httpBasic": {"type": "http", "scheme": "basic"},
                    "httpBearer": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    },
                    "oauth2": {
                        "type": "oauth2",
                        "flows": {
                            "password": {
                                "tokenUrl": "https://auth.example.test/token",
                                "scopes": {"read": "Read protected data"},
                            }
                        },
                    },
                    "openIdConnect": {
                        "type": "openIdConnect",
                        "openIdConnectUrl": "https://auth.example.test/.well-known/openid-configuration",
                    },
                    "reference": {"$ref": "#/components/securitySchemes/apiKey"},
                }
            },
        },
        "components-security-scheme-invalid": {
            "args": [],
            "kwargs": {"securitySchemes": {"unknown": {"type": "custom", "name": "X-Custom"}}},
        },
    }
