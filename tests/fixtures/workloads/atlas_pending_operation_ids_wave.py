"""Independent router tree for custom OpenAPI operation-ID workflows."""

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute


def _application_id(route: APIRoute) -> str:
    return f"app_{route.name}"


def _router_id(route: APIRoute) -> str:
    return f"router_{route.name}"


def _override_id(route: APIRoute) -> str:
    return f"override_{route.name}"


def _duplicate_id(route: APIRoute) -> str:
    del route
    return "shared_operation"


def create_app() -> FastAPI:
    app = FastAPI(generate_unique_id_function=_application_id)

    @app.get("/application-default")
    def application_default():
        return {"route": "application-default"}

    inherited = APIRouter()

    @inherited.get("/router-default")
    def router_default():
        return {"route": "router-default"}

    app.include_router(inherited, prefix="/inherited")

    router_default_ids = APIRouter(generate_unique_id_function=_router_id)

    @router_default_ids.get("/router-default")
    def router_level_default():
        return {"route": "router-level-default"}

    app.include_router(router_default_ids, prefix="/router")

    include_override = APIRouter(generate_unique_id_function=_router_id)

    @include_override.get("/included")
    def include_level_route():
        return {"route": "include-level-override"}

    app.include_router(
        include_override,
        prefix="/include-override",
        generate_unique_id_function=_override_id,
    )

    nested_parent = APIRouter()
    nested_child = APIRouter(generate_unique_id_function=_router_id)

    @nested_parent.get("/parent")
    def nested_parent_route():
        return {"route": "nested-parent"}

    @nested_child.get("/child")
    def nested_child_route():
        return {"route": "nested-child"}

    nested_parent.include_router(nested_child)
    app.include_router(
        nested_parent,
        prefix="/nested",
        generate_unique_id_function=_override_id,
    )

    @app.get("/application-local-override", generate_unique_id_function=_override_id)
    def application_local_override():
        return {"route": "application-local-override"}

    local_override = APIRouter(generate_unique_id_function=_router_id)

    @local_override.get("/router-local-override", generate_unique_id_function=_override_id)
    def router_local_override():
        return {"route": "router-local-override"}

    app.include_router(local_override, prefix="/local-override")

    callback_routes = APIRouter(generate_unique_id_function=_router_id)

    @callback_routes.post("{$hook}/notices", generate_unique_id_function=_override_id)
    def callback_notice():
        return {"accepted": True}

    @app.post(
        "/callback-owner",
        callbacks=callback_routes.routes,
        generate_unique_id_function=_override_id,
    )
    def callback_owner():
        return {"accepted": True}

    duplicates = APIRouter(generate_unique_id_function=_duplicate_id)

    @duplicates.get("/first")
    def first_duplicate():
        return {"route": "first"}

    @duplicates.get("/second")
    def second_duplicate():
        return {"route": "second"}

    app.include_router(duplicates, prefix="/duplicates")
    return app
