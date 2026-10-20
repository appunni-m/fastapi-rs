"""Observe APIRouter.tags identity, mutation, reassignment, and route snapshots."""

from typing import Any

from fastapi import APIRouter, FastAPI


def create_app(_factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    initial_tags = ["initial"]
    router = APIRouter(tags=initial_tags)
    event_trace.append(f"initial:{router.tags is initial_tags}:{router.tags!r}")

    @router.get("/before", tags=["operation"])
    def read_before():
        return {"route": "before"}

    initial_tags.append("mutated")
    event_trace.append(f"mutated:{router.tags is initial_tags}:{router.tags!r}")

    @router.get("/after-mutation", tags=["operation"])
    def read_after_mutation():
        return {"route": "after-mutation"}

    assigned_tags = ["assigned"]
    router.tags = assigned_tags
    event_trace.append(f"assigned:{router.tags is assigned_tags}:{router.tags!r}")

    @router.get("/after-assignment", tags=["operation"])
    def read_after_assignment():
        return {"route": "after-assignment"}

    assigned_tags.append("after-registration")
    event_trace.append(f"assigned-mutated:{router.tags is assigned_tags}:{router.tags!r}")

    app = FastAPI()
    app.include_router(router)
    return app
