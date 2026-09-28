"""Input workload for nested APIRouter response-class inheritance."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse


class OverrideResponse(JSONResponse):
    media_type = "application/x-override"


def create_app() -> FastAPI:
    app = FastAPI()
    router_a = APIRouter()
    router_a_a = APIRouter()
    router_a_b_override = APIRouter()
    router_b_override = APIRouter()
    router_b_a = APIRouter()
    router_b_a_c_override = APIRouter()

    @app.get("/")
    def get_root():
        return {"msg": "Hello World"}

    @app.get("/override", response_class=PlainTextResponse)
    def get_path_override():
        return "Hello World"

    @router_a.get("/")
    def get_a():
        return {"msg": "Hello A"}

    @router_a.get("/override", response_class=PlainTextResponse)
    def get_a_path_override():
        return "Hello A"

    @router_a_a.get("/")
    def get_a_a():
        return {"msg": "Hello A A"}

    @router_a_a.get("/override", response_class=PlainTextResponse)
    def get_a_a_path_override():
        return "Hello A A"

    @router_a_b_override.get("/")
    def get_a_b():
        return {"msg": "Hello A B"}

    @router_a_b_override.get("/override", response_class=HTMLResponse)
    def get_a_b_path_override():
        return "Hello A B"

    @router_b_override.get("/")
    def get_b():
        return {"msg": "Hello B"}

    @router_b_override.get("/override", response_class=HTMLResponse)
    def get_b_path_override():
        return "Hello B"

    @router_b_a.get("/")
    def get_b_a():
        return {"msg": "Hello B A"}

    @router_b_a.get("/override", response_class=HTMLResponse)
    def get_b_a_path_override():
        return "Hello B A"

    @router_b_a_c_override.get("/")
    def get_b_a_c():
        return {"msg": "Hello B A C"}

    @router_b_a_c_override.get("/override", response_class=OverrideResponse)
    def get_b_a_c_path_override():
        return {"msg": "Hello B A C"}

    router_b_a.include_router(
        router_b_a_c_override, prefix="/c", default_response_class=HTMLResponse
    )
    router_b_override.include_router(router_b_a, prefix="/a")
    router_a.include_router(router_a_a, prefix="/a")
    router_a.include_router(
        router_a_b_override, prefix="/b", default_response_class=PlainTextResponse
    )
    app.include_router(router_a, prefix="/a")
    app.include_router(router_b_override, prefix="/b", default_response_class=PlainTextResponse)
    return app
