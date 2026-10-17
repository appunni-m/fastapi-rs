"""Input-only workload for scalar headers added by dependency overrides."""

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    def original_dependency() -> str:
        return "original"

    @app.get("/value")
    def value(
        replacement_value: Annotated[int, Depends(original_dependency)],
    ) -> dict[str, Any]:
        return {
            "value": replacement_value,
            "events": list(event_trace),
        }

    @app.get("/state", include_in_schema=False)
    def state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    def replacement(replacement_count: Annotated[int, Header()]) -> int:
        event_trace.append("replacement")
        return replacement_count

    app.dependency_overrides[original_dependency] = replacement
    return app
