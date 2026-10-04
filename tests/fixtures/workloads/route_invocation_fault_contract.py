"""Small public route workload for target-only route fault contracts."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.get("/fault")
    async def route() -> dict[str, str]:
        return {"status": "ok"}

    async def request_resource() -> AsyncIterator[str]:
        event_trace.append("dependency-enter")
        try:
            yield "ready"
        finally:
            event_trace.append("dependency-cleanup")

    @app.get("/dependency-fault")
    async def dependency_route(resource: str = Depends(request_resource)) -> dict[str, str]:
        event_trace.append("endpoint")
        return {"resource": resource}

    @app.get("/dependency-state")
    async def dependency_state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    return app
