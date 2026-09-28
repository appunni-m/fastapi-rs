"""Independent ASGI stimuli for router and route registration behavior."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
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

    empty_router = APIRouter()

    @empty_router.get("")
    def read_empty_route():
        return ["ready"]

    app.include_router(empty_router, prefix="/prefix")

    @app.api_route("/items/{item_id}", methods=["GET"])
    def get_item(item_id: str):
        return {"item_id": item_id}

    def get_unannotated_item(item_id: str):
        return {"item_id": item_id}

    app.add_api_route("/items-unannotated/{item_id}", get_unannotated_item)

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
    return app
