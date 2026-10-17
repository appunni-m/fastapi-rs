"""Independent ASGI stimuli for router and route registration behavior."""

from __future__ import annotations

from contextlib import AsyncExitStack

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float | None = None


class TaggedRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def tagged_handler(request):
            response = await original(request)
            response.headers["x-route-class"] = "tagged"
            return response

        return tagged_handler


class RequestResponseRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        route_class_name = type(self).__name__

        async def observed_handler(request: Request):
            response = await original(request)
            response.headers["x-observed-route-class"] = route_class_name
            response.headers["x-observed-request-path"] = request.url.path
            response.headers["x-fastapi-inner-astack"] = str(
                isinstance(request.scope.get("fastapi_inner_astack"), AsyncExitStack)
            ).lower()
            response.headers["x-fastapi-function-astack"] = str(
                isinstance(request.scope.get("fastapi_function_astack"), AsyncExitStack)
            ).lower()
            return response

        return observed_handler


class SyncResponseRoute(APIRoute):
    def get_route_handler(self):
        def sync_handler(request: Request):
            return JSONResponse({"handler": "sync", "path": request.url.path})

        return sync_handler


class SeedDependencyStackScope:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/identity":
            scope["fastapi_inner_astack"] = object()
            scope["fastapi_function_astack"] = object()
        await self.app(scope, receive, send)


class RouteA(RequestResponseRoute):
    pass


class RouteB(RequestResponseRoute):
    pass


class RouteC(RequestResponseRoute):
    pass


def _route_class_observation(
    router: APIRouter,
    route_class: type[APIRoute],
) -> dict[str, object]:
    route = router.routes[0]
    return {
        "configured_class": router.route_class.__name__,
        "configured_class_identity": router.route_class is route_class,
        "route_class": type(route).__name__,
        "route_class_identity": type(route) is route_class,
        "route_isinstance": isinstance(route, route_class),
    }


def create_app() -> FastAPI:
    app = FastAPI()

    outer_router = APIRouter(route_class=TaggedRoute)
    middle_router = APIRouter()
    inner_router = APIRouter()

    @outer_router.get("/")
    def read_outer():
        return {"route": "outer"}

    @middle_router.get("/")
    def read_middle():
        return {"route": "middle"}

    @inner_router.get("/")
    def read_inner():
        return {"route": "inner"}

    middle_router.include_router(inner_router, prefix="/c")
    outer_router.include_router(middle_router, prefix="/b")
    app.include_router(outer_router, prefix="/a")

    identity_outer_router = APIRouter(route_class=RouteA)
    identity_middle_router = APIRouter(route_class=RouteB)
    identity_inner_router = APIRouter(route_class=RouteC)

    @identity_outer_router.get("/")
    def read_identity_outer():
        return {"route": "outer"}

    @identity_middle_router.get("/")
    def read_identity_middle():
        return {"route": "middle"}

    @identity_inner_router.get("/")
    def read_identity_inner():
        return {"route": "inner"}

    @identity_inner_router.get("/status-zero", response_model=Item, status_code=0)
    def read_identity_status_zero():
        return {"name": "status-zero"}

    identity_middle_router.include_router(identity_inner_router, prefix="/c")
    identity_outer_router.include_router(identity_middle_router, prefix="/b")
    app.include_router(identity_outer_router, prefix="/identity")

    sync_router = APIRouter(route_class=SyncResponseRoute)

    @sync_router.get("/")
    def sync_route_endpoint():
        return {"handler": "endpoint"}

    app.include_router(sync_router, prefix="/sync-handler")

    @app.get("/route-class-identities")
    def route_class_identities() -> dict[str, object]:
        return {
            "outer": _route_class_observation(identity_outer_router, RouteA),
            "middle": _route_class_observation(identity_middle_router, RouteB),
            "inner": _route_class_observation(identity_inner_router, RouteC),
        }

    empty_router = APIRouter()

    @empty_router.get("")
    def read_empty_route():
        return ["ready"]

    app.include_router(empty_router, prefix="/prefix")

    @app.api_route(
        "/items/{item_id}",
        methods=["GET"],
    )
    def get_item(item_id: str):
        return {"item_id": item_id}

    def get_unannotated_item(item_id: str):
        return {"item_id": item_id}

    app.add_api_route(
        "/items-unannotated/{item_id}",
        get_unannotated_item,
    )

    @app.delete("/items/{item_id}")
    def delete_item(item_id: str, item: Item):
        return {"item_id": item_id, "item": item}

    @app.head("/items/{item_id}")
    def head_item(item_id: str):
        return JSONResponse(None, headers={"x-item-id": item_id})

    @app.options("/items/{item_id}")
    def options_item(item_id: str):
        return JSONResponse(None, headers={"x-item-id": item_id})

    @app.patch("/items/{item_id}")
    def patch_item(item_id: str, item: Item):
        return {"item_id": item_id, "item": item}

    @app.trace("/items/{item_id}")
    def trace_item(item_id: str):
        return JSONResponse(None, media_type="message/http")

    template_router = APIRouter()

    @template_router.get("/users/{user_id}")
    def read_template_user(segment: str, user_id: str):
        return {"segment": segment, "user_id": user_id}

    app.include_router(template_router, prefix="/{segment}")
    app.add_middleware(SeedDependencyStackScope)
    return app
