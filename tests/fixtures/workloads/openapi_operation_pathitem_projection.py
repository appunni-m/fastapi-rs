"""Input-only constructor bundles for the pinned OpenAPI Operation and PathItem models."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "operation-defaults": {"args": [], "kwargs": {}},
        "operation-populated": {
            "args": [],
            "kwargs": {
                "tags": ["widgets", "read"],
                "summary": "List widgets",
                "description": "Return the visible widgets.",
                "externalDocs": {
                    "description": "Widget API reference",
                    "url": "https://example.test/docs/widgets",
                },
                "operationId": "listWidgets",
                "parameters": [{"$ref": "#/components/parameters/limit"}],
                "requestBody": {
                    "description": "Widget filter",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"active": {"type": "boolean"}},
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Widget collection",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            }
                        },
                    }
                },
                "callbacks": {"onChanged": {"$ref": "#/components/callbacks/widgetChanged"}},
                "deprecated": False,
                "security": [{"widgetsOAuth": ["widgets:read"]}],
                "servers": [
                    {
                        "url": "https://api.example.test/v1",
                        "description": "Primary API",
                    }
                ],
                "x-operation-owner": "input-defined",
            },
        },
        "operation-invalid-deprecated": {
            "args": [],
            "kwargs": {"deprecated": "sometimes"},
        },
        "path-item-defaults": {"args": [], "kwargs": {}},
        "path-item-populated": {
            "args": [],
            "kwargs": {
                "$ref": "#/components/pathItems/Widget",
                "summary": "Widget operations",
                "description": "Operations over one widget.",
                "get": {
                    "operationId": "getWidget",
                    "responses": {"200": {"description": "Widget"}},
                },
                "put": {"operationId": "replaceWidget"},
                "post": {"operationId": "createWidget"},
                "delete": {"operationId": "deleteWidget"},
                "options": {"operationId": "optionsWidget"},
                "head": {"operationId": "headWidget"},
                "patch": {"operationId": "patchWidget"},
                "trace": {"operationId": "traceWidget"},
                "servers": [{"url": "https://api.example.test/v1"}],
                "parameters": [{"$ref": "#/components/parameters/widgetId"}],
                "x-path-item-owner": "input-defined",
            },
        },
        "path-item-invalid-summary": {
            "args": [],
            "kwargs": {"summary": ["not", "a", "string"]},
        },
    }
