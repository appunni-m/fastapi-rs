"""Input-driven callback return values and failures for operation IDs."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    behavior = factory_input["behavior"]

    def generate(route: Any) -> Any:
        del route
        if behavior == "integer":
            return 17
        if behavior == "empty":
            return ""
        if behavior == "unhashable":
            return []
        if behavior == "error":
            raise LookupError("unique ID callback failed")
        raise AssertionError(f"unknown callback behavior: {behavior}")

    app = FastAPI()
    if behavior == "error":

        @app.get("/trigger", operation_id="trigger")
        def trigger() -> dict[str, str]:
            app.add_api_route(
                "/late", lambda: {"value": "ok"}, generate_unique_id_function=generate
            )
            return {"value": "ok"}
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
        return {
            "unique_id": next(route.unique_id for route in app.routes if route.path == "/value")
        }

    return app
