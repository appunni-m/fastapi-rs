"""Drive FastAPI 0.141.1 APIRoute instances as standalone ASGI applications.

FastAPI 0.141.1 builds APIRoute.app in fastapi/routing.py:1161-1223.
Starlette 1.6.0 BaseRoute.__call__ performs matching in
starlette/routing.py:177-194 and Route.handle handles method mismatch in
starlette/routing.py:271-280. The per-request exit stack supplies the FastAPI
middleware stack required at fastapi/routing.py:406-411; ``APIRoute.app``
creates the inner and function dependency stacks itself. This workload does not
create or register a FastAPI application.
"""

from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any, Callable

from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field


class ItemResponse(BaseModel):
    item_id: int
    label: str


class FilteredResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str = Field(alias="displayName")
    visible: str
    internal_token: str
    state: str = "draft"
    note: str | None = None
    not_supplied: str = "omitted-default"


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> Callable[..., Any]:
    """Construct one APIRoute from recipe inputs and return its ASGI call."""
    del event_trace

    response_models: dict[str, type[BaseModel]] = {
        "item": ItemResponse,
        "filtered": FilteredResponse,
    }

    if factory_input["endpoint"] == "item":

        async def endpoint(item_id: int) -> dict[str, Any]:
            return {"item_id": item_id, "label": factory_input["label"]}
    else:

        async def endpoint() -> dict[str, Any]:
            return factory_input["response"]

    route_options: dict[str, Any] = {}
    if "response_model_include" in factory_input:
        route_options["response_model_include"] = set(factory_input["response_model_include"])
    if "response_model_exclude" in factory_input:
        route_options["response_model_exclude"] = set(factory_input["response_model_exclude"])
    if "response_model_by_alias" in factory_input:
        route_options["response_model_by_alias"] = factory_input["response_model_by_alias"]
    if "response_model_exclude_unset" in factory_input:
        route_options["response_model_exclude_unset"] = factory_input[
            "response_model_exclude_unset"
        ]
    if "response_model_exclude_defaults" in factory_input:
        route_options["response_model_exclude_defaults"] = factory_input[
            "response_model_exclude_defaults"
        ]
    if "response_model_exclude_none" in factory_input:
        route_options["response_model_exclude_none"] = factory_input["response_model_exclude_none"]

    route = APIRoute(
        factory_input["route_path"],
        endpoint,
        methods=factory_input["methods"],
        response_model=response_models[factory_input["response_model"]],
        **route_options,
    )

    async def standalone_route(scope: Any, receive: Any, send: Any) -> None:
        async with AsyncExitStack() as stack:
            scope["fastapi_middleware_astack"] = stack
            await route(scope, receive, send)

    return standalone_route
