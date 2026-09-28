"""Input workload for metadata inherited across nested router inclusion."""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse


def create_app() -> FastAPI:
    def dependency_a():
        return "a"

    def dependency_b():
        return "b"

    def dependency_c():
        return "c"

    def unique_id_b(route) -> str:
        return f"b_{route.name}"

    callback_router = APIRouter()

    @callback_router.post("/callback")
    def callback():
        return {"ok": True}

    callback_route = callback_router.routes[0]
    parent_router = APIRouter()
    included_router = APIRouter(
        prefix="/items",
        tags=["router"],
        dependencies=[Depends(dependency_a)],
        responses={401: {"description": "Unauthorized"}},
        callbacks=[callback_route],
        default_response_class=HTMLResponse,
        strict_content_type=False,
    )

    @included_router.get(
        "/{item_id}",
        tags=["route"],
        dependencies=[Depends(dependency_b)],
        responses={404: {"description": "Missing"}},
        callbacks=[callback_route],
        generate_unique_id_function=unique_id_b,
    )
    def read_item(item_id: str, request: Request):
        context = request.scope["fastapi"]["effective_route_context"]
        return JSONResponse(
            {
                "path": context.path,
                "tags": context.tags,
                "dependency_count": len(context.dependencies),
                "response_codes": sorted(context.responses),
                "callback_count": len(context.callbacks or []),
                "deprecated": context.deprecated,
                "include_in_schema": context.include_in_schema,
                "response_class": context.response_class.__name__,
                "generate_unique_id": context.generate_unique_id_function(context),
                "strict_content_type": context.strict_content_type,
                "has_dependency_overrides_provider": (
                    context.dependency_overrides_provider
                    is app.router.dependency_overrides_provider
                ),
            }
        )

    parent_router.include_router(
        included_router,
        prefix="/api",
        tags=["include"],
        dependencies=[Depends(dependency_c)],
        responses={400: {"description": "Bad request"}},
        callbacks=[callback_route],
        deprecated=True,
        include_in_schema=False,
    )

    app = FastAPI()
    app.include_router(parent_router)
    return app
