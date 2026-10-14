"""Input-only direct constructor bundles for the public OpenAPI Schema model."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "schema-alias-wire": {
            "args": [],
            "kwargs": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$vocabulary": "https://example.test/vocabulary",
                "$id": "https://example.test/schema",
                "$anchor": "root",
                "$dynamicAnchor": "node",
                "$ref": "https://example.test/ref",
                "$dynamicRef": "https://example.test/dynamic-ref",
                "$defs": {"AliasProbe": True},
                "$comment": "wire alias input",
                "not": True,
                "if": False,
                "else": {"type": "integer"},
            },
        },
        "schema-python-field-names": {
            "args": [],
            "kwargs": {
                "schema_": "https://json-schema.org/draft/2020-12/schema",
                "vocabulary": "https://example.test/vocabulary",
                "id": "https://example.test/schema",
                "anchor": "root",
                "dynamicAnchor": "node",
                "ref": "https://example.test/ref",
                "dynamicRef": "https://example.test/dynamic-ref",
                "defs": {"AliasProbe": True},
                "comment": "Python-name input",
                "not_": True,
                "if_": False,
                "else_": {"type": "integer"},
            },
        },
        "schema-defaults": {"args": [], "kwargs": {}},
        "schema-invalid-multiple-of": {"args": [], "kwargs": {"multipleOf": 0}},
        "schema-invalid-min-length": {"args": [], "kwargs": {"minLength": -1}},
        "schema-invalid-max-items": {"args": [], "kwargs": {"maxItems": -1}},
    }
