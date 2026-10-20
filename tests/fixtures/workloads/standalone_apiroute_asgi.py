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

from collections.abc import Callable
from contextlib import AsyncExitStack
from types import SimpleNamespace
from typing import Annotated, Any

from fastapi import Depends, File, Form, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field


class ItemResponse(BaseModel):
    item_id: int
    label: str


class BodyItem(BaseModel):
    item_id: int
    label: str


class FormResponse(BaseModel):
    username: str


class FilteredResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str = Field(alias="displayName")
    visible: str
    internal_token: str
    state: str = "draft"
    note: str | None = None
    not_supplied: str = "omitted-default"


class DependencyResponse(BaseModel):
    item_id: int
    dependency_value: str


class DependencyTraceResponse(BaseModel):
    trace: list[str]


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> Callable[..., Any]:
    """Construct one APIRoute from recipe inputs and return its ASGI call."""
    response_models: dict[str, type[BaseModel]] = {
        "item": ItemResponse,
        "body": BodyItem,
        "form": FormResponse,
        "filtered": FilteredResponse,
        "dependency": DependencyResponse,
    }

    route_options: dict[str, Any] = {}
    trace_route: APIRoute | None = None
    if factory_input["endpoint"] == "item":

        async def endpoint(item_id: int) -> dict[str, Any]:
            return {"item_id": item_id, "label": factory_input["label"]}
    elif factory_input["endpoint"] == "dependency":

        async def route_dependency() -> Any:
            event_trace.append("dependency-enter")
            try:
                yield factory_input["dependency_value"]
            finally:
                event_trace.append("dependency-exit")

        async def endpoint(
            item_id: int,
            dependency_value: str = Depends(route_dependency),
        ) -> dict[str, Any]:
            event_trace.append("endpoint")
            return {"item_id": item_id, "dependency_value": dependency_value}

        if factory_input.get("override_dependency"):

            async def override_route_dependency() -> Any:
                event_trace.append("override-enter")
                try:
                    yield factory_input["dependency_override_value"]
                finally:
                    event_trace.append("override-exit")

            route_options["dependency_overrides_provider"] = SimpleNamespace(
                dependency_overrides={route_dependency: override_route_dependency}
            )

        async def trace_endpoint() -> dict[str, Any]:
            return {"trace": list(event_trace)}

        trace_route = APIRoute(
            "/_workload-trace",
            trace_endpoint,
            response_model=DependencyTraceResponse,
        )
        route_options["dependencies"] = [Depends(route_dependency)]
    elif factory_input["endpoint"] == "body":

        async def endpoint(body: BodyItem) -> BodyItem:
            return body
    elif factory_input["endpoint"] == "form":

        async def endpoint(
            username: Annotated[str, Form()],
            password: Annotated[str, Form()],
        ) -> dict[str, str]:
            return {"username": username}
    elif factory_input["endpoint"] == "file-bytes":

        async def endpoint(file: Annotated[bytes, File()]):
            return {"file_size": len(file)}
    elif factory_input["endpoint"] == "upload-file":

        async def endpoint(file: UploadFile):
            return {"filename": file.filename}
    else:

        async def endpoint() -> dict[str, Any]:
            return factory_input["response"]

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

    response_model_name = factory_input.get("response_model")
    if response_model_name is not None:
        route_options["response_model"] = response_models[response_model_name]
    route = APIRoute(
        factory_input["route_path"], endpoint, methods=factory_input["methods"], **route_options
    )

    async def standalone_route(scope: Any, receive: Any, send: Any) -> None:
        trace_action = scope["path"] == "/_workload-trace" and trace_route is not None
        route_to_call: Any = trace_route if trace_action else route
        if factory_input.get("invoke_route_app"):
            route_to_call = route.app
            scope["starlette.exception_handlers"] = (
                {RequestValidationError: request_validation_exception_handler},
                {},
            )

        async def trace_send(message: dict[str, Any]) -> None:
            if factory_input["endpoint"] == "dependency" and not trace_action:
                if message["type"] == "http.response.start":
                    event_trace.append("response-start")
                elif message["type"] == "http.response.body" and not message.get(
                    "more_body", False
                ):
                    event_trace.append("response-body")
            await send(message)

        async with AsyncExitStack() as stack:
            scope["fastapi_middleware_astack"] = stack
            await route_to_call(scope, receive, trace_send)
        if factory_input["endpoint"] == "dependency" and not trace_action:
            event_trace.append("route-return")

    return standalone_route
