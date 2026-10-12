"""Independent multi-method route inputs for unique-ID callback observations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    callback_calls: list[dict[str, Any]] = []

    def generate(route: Any) -> str:
        methods = sorted(route.methods)
        callback_calls.append(
            {"path": route.path, "path_format": route.path_format, "methods": methods}
        )
        return f"{route.path_format}|{'_'.join(methods)}"

    def endpoint() -> dict[str, str]:
        return {"result": "ok"}

    app = FastAPI()
    app.add_api_route(
        "/multi",
        endpoint,
        methods=["GET", "POST"],
        generate_unique_id_function=generate,
    )

    router = APIRouter(generate_unique_id_function=generate)
    router.add_api_route("/included", endpoint, methods=["GET", "POST"])
    app.include_router(router, prefix="/api")

    @app.get("/observe", operation_id="observe")
    def observe() -> dict[str, Any]:
        return {"calls": callback_calls}

    return app
