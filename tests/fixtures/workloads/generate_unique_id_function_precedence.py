"""Isolated inputs for FastAPI operation-ID callback precedence."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI


def _id(prefix: str) -> Any:
    def generate(route: Any) -> str:
        safe_path = route.path_format.strip("/").replace("/", "_") or "root"
        responses = ",".join(
            f"{status}:{response.get('description', '')}"
            for status, response in sorted(route.responses.items(), key=lambda item: str(item[0]))
        )
        tags = ",".join(route.tags)
        return (
            f"{prefix}_{route.name}_{safe_path}"
            f"__summary={route.summary or '-'}"
            f"__response={route.response_description}"
            f"__responses={responses or '-'}"
            f"__deprecated={route.deprecated}"
            f"__schema={route.include_in_schema}"
            f"__tags={tags or '-'}"
        )

    return generate


def create_app() -> FastAPI:
    app = FastAPI(generate_unique_id_function=_id("app"))

    @app.get(
        "/app-default",
        summary="Application route",
        response_description="Application result",
        responses={201: {"description": "created"}},
        deprecated=False,
        tags=["application"],
    )
    def app_default() -> dict[str, str]:
        return {"scope": "app"}

    include_router = APIRouter()

    @include_router.get(
        "/include-default",
        summary="Included route",
        response_description="Included result",
        responses={202: {"description": "accepted"}},
        tags=["local"],
    )
    def include_default() -> dict[str, str]:
        return {"scope": "include"}

    app.include_router(
        include_router,
        generate_unique_id_function=_id("include"),
        deprecated=True,
        tags=["included"],
    )

    parent = APIRouter(
        prefix="/tree",
        generate_unique_id_function=_id("parent"),
    )

    @parent.get("/parent")
    def parent_route() -> dict[str, str]:
        return {"scope": "parent"}

    leaf = APIRouter(generate_unique_id_function=_id("leaf"))

    @leaf.get("/route")
    def leaf_route() -> dict[str, str]:
        return {"scope": "leaf"}

    @leaf.get("/route-override", generate_unique_id_function=_id("route"))
    def route_override() -> dict[str, str]:
        return {"scope": "route"}

    parent.include_router(
        leaf,
        prefix="/leaf",
        generate_unique_id_function=_id("nested-include"),
    )
    app.include_router(
        parent,
        generate_unique_id_function=_id("app-include"),
    )
    return app
