"""Input workload for body fields inherited from app, router, and include."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, FastAPI


def create_app() -> FastAPI:
    def app_body_dependency(app_body: Annotated[str, Body()]):
        return app_body

    def router_body_dependency(router_body: Annotated[int, Body()]):
        return router_body

    def include_body_dependency(include_body: Annotated[bool, Body()]):
        return include_body

    app = FastAPI(dependencies=[Depends(app_body_dependency)])
    router = APIRouter(dependencies=[Depends(router_body_dependency)])

    @router.post("/items")
    def create_item(route_body: Annotated[float, Body()]):
        return {"route_body": route_body}

    app.include_router(
        router,
        prefix="/api",
        dependencies=[Depends(include_body_dependency)],
    )
    return app
