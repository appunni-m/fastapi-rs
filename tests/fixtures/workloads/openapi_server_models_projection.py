"""Input-only constructor bundles for direct OpenAPI server model probes."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "server-missing-url": {"args": [], "kwargs": {}},
        "server-defaults": {
            "args": [],
            "kwargs": {"url": "https://api.example.test/v1"},
        },
        "server-nested-variables-extra": {
            "args": [],
            "kwargs": {
                "url": "https://api.example.test/{environment}",
                "description": "Regional API server",
                "variables": {
                    "environment": {
                        "default": "staging",
                        "description": "Deployment environment",
                        "enum": ["development", "staging", "production"],
                        "x-variable-extension": "variable-level",
                    }
                },
                "x-server-extension": "server-level",
            },
        },
        "server-variable-missing-default": {"args": [], "kwargs": {}},
        "server-variable-defaults": {
            "args": [],
            "kwargs": {"default": "production"},
        },
        "server-variable-extra": {
            "args": [],
            "kwargs": {
                "default": "staging",
                "description": "Deployment environment",
                "enum": ["development", "staging", "production"],
                "x-variable-extension": "variable-level",
            },
        },
        "server-variable-empty-enum": {
            "args": [],
            "kwargs": {"default": "staging", "enum": []},
        },
    }
