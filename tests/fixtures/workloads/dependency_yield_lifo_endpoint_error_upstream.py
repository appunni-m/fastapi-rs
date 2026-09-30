"""Input-only probe for nested yield-dependency cleanup after endpoint failure."""

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input
    app = FastAPI()

    async def parent_dependency():
        parent = {"phase": "active"}
        event_trace.append("parent-enter")
        try:
            yield parent
        finally:
            parent["phase"] = "closed"
            event_trace.append("parent-exit")

    async def child_dependency(parent: Annotated[dict[str, str], Depends(parent_dependency)]):
        event_trace.append("child-enter")
        try:
            yield parent
        finally:
            event_trace.append(f"child-exit:{parent['phase']}")

    @app.get("/nested-failure")
    async def nested_failure(
        state: Annotated[dict[str, str], Depends(child_dependency)],
    ) -> None:
        assert state["phase"] == "active"
        event_trace.append("endpoint-raise")
        raise RuntimeError("endpoint failed")

    @app.get("/events")
    def observed_events() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    return app
