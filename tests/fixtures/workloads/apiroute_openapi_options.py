"""Input-only APIRoute constructor options for direct API parity."""

from __future__ import annotations

from fastapi.routing import APIRoute
from pydantic import BaseModel


class Item(BaseModel):
    item_id: int
    label: str


def configured_item() -> Item:
    return Item(item_id=7, label="seven")


def annotated_item() -> Item:
    return Item(item_id=8, label="eight")


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build fresh route objects from public constructor arguments."""
    configured_route = APIRoute(
        "/direct-items",
        configured_item,
        response_model=Item,
        status_code=201,
        tags=["catalog"],
        summary="Create an item",
        name="create_item",
        methods=["post"],
    )
    disabled_model_route = APIRoute(
        "/annotated-items",
        annotated_item,
        response_model=None,
    )
    return {
        "configured-route": {
            "args": ["/direct-items", configured_item],
            "kwargs": {
                "response_model": Item,
                "status_code": 201,
                "tags": ["catalog"],
                "summary": "Create an item",
                "name": "create_item",
                "methods": ["post"],
            },
        },
        "configured-openapi": {
            "args": [],
            "kwargs": {
                "title": "Configured APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [configured_route],
            },
        },
        "disabled-model-route": {
            "args": ["/annotated-items", annotated_item],
            "kwargs": {"response_model": None},
        },
        "disabled-model-openapi": {
            "args": [],
            "kwargs": {
                "title": "Disabled Response Model OpenAPI Probe",
                "version": "1.0.0",
                "routes": [disabled_model_route],
            },
        },
    }
