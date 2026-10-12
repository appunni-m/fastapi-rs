"""Input-driven callback return values and failures for operation IDs."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class CallbackItem(BaseModel):
    name: str
    secret: str


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    behavior = factory_input["behavior"]
    callback_snapshot: dict[str, Any] | None = None

    def generate(route: Any) -> Any:
        nonlocal callback_snapshot
        if behavior == "integer":
            return 17
        if behavior == "empty":
            return ""
        if behavior == "unhashable":
            return []
        if behavior == "error":
            raise LookupError("unique ID callback failed")
        if behavior == "router-flags":
            return f"{route.deprecated!r}:{route.include_in_schema!r}:{route.path}"
        if behavior == "router-add-api-route":
            return (
                f"{route.deprecated!r}:{route.include_in_schema!r}:"
                f"{route.path}:{','.join(route.tags)}"
            )
        if behavior == "app-add-api-route":
            return (
                f"{route.deprecated!r}:{route.include_in_schema!r}:"
                f"{route.path}:{','.join(route.tags)}"
            )
        if behavior == "mutation":
            route.summary = "callback summary"
            route.tags.append("callback-tag")
            return f"{route.summary}:{','.join(route.tags)}"
        if behavior == "callback-state":
            response_class = route.response_class
            strict_content_type = route.strict_content_type
            callback_snapshot = {
                "path": route.path,
                "path_format": route.path_format,
                "path_regex": route.path_regex.pattern,
                "param_convertors": {
                    name: type(convertor).__name__
                    for name, convertor in route.param_convertors.items()
                },
                "methods": sorted(route.methods),
                "name": route.name,
                "summary": route.summary,
                "response_description": route.response_description,
                "deprecated": route.deprecated,
                "include_in_schema": route.include_in_schema,
                "operation_id": route.operation_id,
                "response_model_include": sorted(route.response_model_include),
                "response_model_exclude": sorted(route.response_model_exclude),
                "response_model_by_alias": route.response_model_by_alias,
                "response_model_exclude_unset": route.response_model_exclude_unset,
                "response_model_exclude_defaults": route.response_model_exclude_defaults,
                "response_model_exclude_none": route.response_model_exclude_none,
                "response_class_type": type(response_class).__name__,
                "response_class_value": response_class.value.__name__,
                "dependency_overrides_provider_is_app": route.dependency_overrides_provider is app,
                "callbacks": route.callbacks,
                "strict_content_type": (
                    strict_content_type.value
                    if type(strict_content_type).__name__ == "DefaultPlaceholder"
                    else strict_content_type
                ),
                "stream_item_type": route.stream_item_type,
                "late_attributes_absent": {
                    name: not hasattr(route, name)
                    for name in (
                        "unique_id",
                        "status_code",
                        "dependencies",
                        "description",
                        "response_model",
                        "response_field",
                        "app",
                    )
                },
            }
            return json.dumps(callback_snapshot, sort_keys=True)
        raise AssertionError(f"unknown callback behavior: {behavior}")

    app = FastAPI()
    router_route = None
    mutated_route = None
    if behavior == "error":

        @app.get("/trigger", operation_id="trigger")
        def trigger() -> dict[str, str]:
            app.add_api_route(
                "/late", lambda: {"value": "ok"}, generate_unique_id_function=generate
            )
            return {"value": "ok"}
    elif behavior == "router-flags":
        router = APIRouter(
            deprecated=False,
            include_in_schema=False,
            generate_unique_id_function=generate,
        )
        router.get("/hidden")(lambda: {"value": "hidden"})
        router_route = router.routes[0]
        app.include_router(router, prefix="/api")
    elif behavior == "router-add-api-route":
        router = APIRouter(
            tags=["router-tag"],
            deprecated=False,
            include_in_schema=False,
            generate_unique_id_function=generate,
        )
        router.add_api_route(
            "/hidden",
            lambda: {"value": "hidden"},
            tags=["route-tag"],
        )
        router_route = router.routes[0]
        app.include_router(router, prefix="/api")
    elif behavior == "app-add-api-route":
        app.add_api_route(
            "/hidden",
            lambda: {"value": "hidden"},
            deprecated=False,
            include_in_schema=False,
            tags=["route-tag"],
            generate_unique_id_function=generate,
        )
        router_route = next(route for route in app.routes if route.path == "/hidden")
    elif behavior == "mutation":
        app.get(
            "/mutated",
            summary="before callback",
            tags=["source-tag"],
            generate_unique_id_function=generate,
        )(lambda: {"value": "ok"})
        mutated_route = next(route for route in app.routes if route.path == "/mutated")
    elif behavior == "callback-state":

        @app.get(
            "/callback-state/{item_id}",
            response_model=CallbackItem,
            response_model_include={"name"},
            response_model_exclude={"secret"},
            response_model_by_alias=False,
            response_model_exclude_unset=True,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True,
            generate_unique_id_function=generate,
        )
        def callback_state_endpoint(item_id: str) -> CallbackItem:
            return CallbackItem(name=item_id, secret="hidden")
    else:
        app.get(
            "/value",
            operation_id=factory_input.get("operation_id"),
            generate_unique_id_function=generate,
        )(lambda: {"value": "ok"})
        if factory_input.get("duplicate", False):
            app.get("/second", generate_unique_id_function=generate)(lambda: {"value": "ok"})

    @app.get("/observe", operation_id="observe")
    def observe() -> dict[str, Any]:
        if router_route is not None:
            return {
                "deprecated": router_route.deprecated,
                "include_in_schema": router_route.include_in_schema,
                "tags": router_route.tags,
                "unique_id": router_route.unique_id,
            }
        if mutated_route is not None:
            return {
                "summary": mutated_route.summary,
                "tags": mutated_route.tags,
                "unique_id": mutated_route.unique_id,
            }
        if callback_snapshot is not None:
            return callback_snapshot
        return {
            "unique_id": next(route.unique_id for route in app.routes if route.path == "/value")
        }

    return app
