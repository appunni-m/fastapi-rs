"""Input-only workload for response-class mutation around router inclusion."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse


class IncludedResponse(JSONResponse):
    media_type = "application/x-included+json"


class LateResponse(JSONResponse):
    media_type = "application/x-late+json"


class AfterObservationResponse(JSONResponse):
    media_type = "application/x-after-observation+json"


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    del event_trace

    router = APIRouter()

    @router.get("/items")
    def get_items() -> dict[str, str]:
        return {"source": "router"}

    @router.get("/groups")
    def get_groups() -> dict[str, str]:
        return {"source": "sibling"}

    app = FastAPI()
    app.include_router(router, default_response_class=IncludedResponse)

    if factory_input["materialize_before_mutation"] == "true":
        app.openapi()

    router.default_response_class = LateResponse
    if factory_input["observe_contexts_after_mutation"] == "true":
        from fastapi.routing import iter_route_contexts

        route_contexts = iter_route_contexts(app.routes)
        next(context for context in route_contexts if context.path == "/items")
        router.default_response_class = AfterObservationResponse
        next(context for context in route_contexts if context.path == "/groups")
    return app
