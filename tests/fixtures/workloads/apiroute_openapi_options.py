"""Input-only APIRoute constructor options for direct API parity."""

from __future__ import annotations

from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel


class Item(BaseModel):
    item_id: int
    label: str


def configured_item() -> Item:
    return Item(item_id=7, label="seven")


def annotated_item() -> Item:
    return Item(item_id=8, label="eight")


def plain_text_item() -> str:
    return "seven"


def custom_unique_id(route: APIRoute) -> str:
    return f"custom-{route.name}"


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build fresh route objects from public constructor arguments."""
    configured_route = APIRoute(
        "/direct-items",
        configured_item,
        response_model=Item,
        status_code=201,
        response_description="The item was created",
        responses={409: {"description": "The item already exists"}},
        deprecated=True,
        operation_id="create_configured_item",
        openapi_extra={"x-fastapi-rs-probe": {"route": "configured"}},
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
    hidden_route = APIRoute(
        "/hidden-items",
        annotated_item,
        include_in_schema=False,
    )
    callback_id_route = APIRoute(
        "/callback-items",
        configured_item,
        name="callback_item",
        generate_unique_id_function=custom_unique_id,
    )
    plain_text_route = APIRoute(
        "/direct-text",
        plain_text_item,
        response_class=PlainTextResponse,
    )
    filtered_route = APIRoute(
        "/filtered-items",
        configured_item,
        response_model=Item,
        response_model_include={"item_id"},
        response_model_exclude={"label"},
        response_model_by_alias=False,
        response_model_exclude_unset=True,
        response_model_exclude_defaults=True,
        response_model_exclude_none=True,
    )
    return {
        "configured-route": {
            "args": ["/direct-items", configured_item],
            "kwargs": {
                "response_model": Item,
                "status_code": 201,
                "response_description": "The item was created",
                "responses": {409: {"description": "The item already exists"}},
                "deprecated": True,
                "operation_id": "create_configured_item",
                "openapi_extra": {"x-fastapi-rs-probe": {"route": "configured"}},
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
        "hidden-route": {
            "args": ["/hidden-items", annotated_item],
            "kwargs": {"include_in_schema": False},
        },
        "hidden-openapi": {
            "args": [],
            "kwargs": {
                "title": "Hidden APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [hidden_route],
            },
        },
        "callback-id-route": {
            "args": ["/callback-items", configured_item],
            "kwargs": {
                "name": "callback_item",
                "generate_unique_id_function": custom_unique_id,
            },
        },
        "callback-id-openapi": {
            "args": [],
            "kwargs": {
                "title": "Callback APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [callback_id_route],
            },
        },
        "plain-text-route": {
            "args": ["/direct-text", plain_text_item],
            "kwargs": {"response_class": PlainTextResponse},
        },
        "plain-text-openapi": {
            "args": [],
            "kwargs": {
                "title": "Plain Text APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [plain_text_route],
            },
        },
        "filtered-route": {
            "args": ["/filtered-items", configured_item],
            "kwargs": {
                "response_model": Item,
                "response_model_include": {"item_id"},
                "response_model_exclude": {"label"},
                "response_model_by_alias": False,
                "response_model_exclude_unset": True,
                "response_model_exclude_defaults": True,
                "response_model_exclude_none": True,
            },
        },
        "filtered-openapi": {
            "args": [],
            "kwargs": {
                "title": "Filtered APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [filtered_route],
            },
        },
    }
