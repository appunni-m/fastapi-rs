"""Input-only APIRoute response-class field and dispatch observations."""

from __future__ import annotations

import json
from contextlib import AsyncExitStack
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute
from starlette.requests import Request


def _qualified_name(value: Any) -> str:
    return f"{value.__module__}.{value.__qualname__}"


def _response_class_value(response_class: Any) -> dict[str, Any]:
    is_placeholder = hasattr(response_class, "value")
    value = response_class.value if is_placeholder else response_class
    return {
        "field_type": _qualified_name(type(response_class)),
        "field_value": _qualified_name(value),
        "is_default_placeholder": is_placeholder,
        "value_is_json_response": value is JSONResponse,
        "value_is_plain_text_response": value is PlainTextResponse,
    }


def _request_handler_asgi_app(handler: Any) -> Any:
    async def app(scope: Any, receive: Any, send: Any) -> None:
        request = Request(scope, receive, send)
        async with AsyncExitStack() as request_stack:
            scope["fastapi_inner_astack"] = request_stack
            async with AsyncExitStack() as function_stack:
                scope["fastapi_function_astack"] = function_stack
                response = await handler(request)
            await response(scope, receive, send)

    return app


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> Any:
    del event_trace
    mode = factory_input["mode"]
    route_reference: dict[str, APIRoute] = {}

    def endpoint() -> str:
        return json.dumps(
            _response_class_value(route_reference["route"].response_class),
            sort_keys=True,
            separators=(",", ":"),
        )

    if mode == "direct-default":
        route = APIRoute("/", endpoint)
        route_reference["route"] = route
        return FastAPI(routes=[route])

    if mode == "direct-plain-text":
        route = APIRoute("/", endpoint, response_class=PlainTextResponse)
        route_reference["route"] = route
        return FastAPI(routes=[route])

    if mode == "router-default":
        router = APIRouter(default_response_class=PlainTextResponse)
        router.add_api_route("/", endpoint)
        route_reference["route"] = router.routes[-1]
        app = FastAPI()
        app.include_router(router)
        return app

    if mode in {"direct-mutated-handler-rebuild", "direct-mutated-old-app"}:
        route = APIRoute("/", endpoint)
        route_reference["route"] = route
        old_app = route.app
        route.response_class = PlainTextResponse
        if mode == "direct-mutated-handler-rebuild":
            route.app = _request_handler_asgi_app(route.get_route_handler())
        else:
            route.app = old_app
        return FastAPI(routes=[route])

    raise ValueError(f"unknown response-class probe mode: {mode}")
