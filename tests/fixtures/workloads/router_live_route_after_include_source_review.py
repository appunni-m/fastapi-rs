"""Independent stimulus for a route added after its router was included."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    dependency_calls: list[str] = []

    def included_dependency() -> None:
        dependency_calls.append("included")

    router = APIRouter()
    app = FastAPI()
    app.include_router(
        router,
        prefix="/catalog",
        tags=["deferred"],
        dependencies=[Depends(included_dependency)],
        responses={429: {"description": "Retry later."}},
    )

    @router.get("/jobs")
    def read_jobs() -> dict[str, Any]:
        return {"dependency_runs": len(dependency_calls), "job": "queued"}

    return app
