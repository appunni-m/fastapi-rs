"""Input-driven callback return values and failures for operation IDs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    behavior = factory_input["behavior"]

    def generate(route: Any) -> Any:
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
        return {
            "unique_id": next(route.unique_id for route in app.routes if route.path == "/value")
        }

    return app
