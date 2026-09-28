"""Independent ASGI stimuli for Starlette routes included through APIRouter."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import PlainTextResponse
from starlette.routing import Host, Mount, Route, Router


def create_app() -> FastAPI:
    app = FastAPI()

    get_router = APIRouter()

    @get_router.get("/items")
    def read_items():
        return {"method": "get"}

    post_router = APIRouter()

    @post_router.post("/items")
    def create_item():
        return {"method": "post"}

    app.include_router(get_router, prefix="/all-match")
    app.include_router(post_router, prefix="/all-match")

    partial_router = APIRouter()

    @partial_router.get("/items")
    def read_partial_items():
        return []

    app.include_router(partial_router, prefix="/partial")

    redirect_router = APIRouter()
    exact_router = APIRouter()

    @redirect_router.get("/items/")
    def read_items_with_slash():
        return {"path": "slash"}

    @exact_router.get("/items")
    def read_items_without_slash():
        return {"path": "exact"}

    app.include_router(redirect_router, prefix="/slash")
    app.include_router(exact_router, prefix="/slash")

    def mounted_endpoint(request):
        url_path = app.url_path_for("mounted:read_item", item_id="abc")
        return PlainTextResponse(f"mounted:{request.path_params['item_id']}:{url_path}")

    mount_router = APIRouter(
        routes=[
            Mount(
                "/mounted",
                routes=[Route("/items/{item_id}", mounted_endpoint, name="read_item")],
                name="mounted",
            )
        ]
    )
    app.include_router(mount_router, prefix="/api")

    def hosted_endpoint(request):
        url_path = app.url_path_for(
            "hosted:read_item",
            subdomain="api",
            item_id=request.path_params["item_id"],
        )
        return PlainTextResponse(f"hosted:{request.path_params['subdomain']}:{url_path}")

    hosted_app = Router(routes=[Route("/items/{item_id}", hosted_endpoint, name="read_item")])
    host_router = APIRouter(routes=[Host("{subdomain}.example.com", hosted_app, name="hosted")])
    app.include_router(host_router, prefix="/api")
    return app
