"""Independent route stimulus for duplicate OpenAPI operation ID warnings."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    def duplicate_id(route: Any) -> str:
        return "duplicate-operation"

    @app.get("/duplicate-first", generate_unique_id_function=duplicate_id)
    def first_endpoint() -> dict[str, str]:
        return {"route": "first"}

    @app.get("/duplicate-second", generate_unique_id_function=duplicate_id)
    def second_endpoint() -> dict[str, str]:
        return {"route": "second"}

    return app
