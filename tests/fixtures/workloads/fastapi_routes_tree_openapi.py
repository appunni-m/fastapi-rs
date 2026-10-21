"""Observe FastAPI's public route tree and its direct OpenAPI input."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def constructor_endpoint(request: Request) -> JSONResponse:
    return JSONResponse({"source": "constructor-route"})


def create_app() -> FastAPI:
    mounted = FastAPI(title="Mounted Route Tree", version="1.0.0")

    @mounted.get("/child")
    def mounted_child() -> dict[str, str]:
        return {"source": "mounted"}

    constructor_routes = [Route("/constructor", constructor_endpoint, name="constructor")]
    app = FastAPI(
        title="Route Tree Input",
        version="1.0.0",
        routes=constructor_routes,
    )
    constructor_routes.clear()

    @app.get("/direct", name="direct")
    def direct_route() -> dict[str, str]:
        return {"source": "direct"}

    router = APIRouter()

    @router.post("/included", name="included")
    def included_route() -> dict[str, str]:
        return {"source": "included"}

    app.include_router(router, prefix="/api")
    app.mount("/mounted", mounted, name="mounted")

    @app.get("/inspect", name="inspect")
    def inspect_route_tree() -> dict[str, object]:
        routes = app.routes
        route_entries = []
        for route in routes:
            methods = getattr(route, "methods", None)
            route_entries.append(
                {
                    "type": type(route).__name__,
                    "path": getattr(route, "path", None),
                    "name": getattr(route, "name", None),
                    "methods": sorted(methods) if methods is not None else None,
                }
            )
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=routes,
        )
        return {
            "route_list_identity_stable": routes is app.routes,
            "router_routes_identity_shared": routes is app.router.routes,
            "constructor_routes_input_copied": routes[0].path == "/constructor",
            "routes": route_entries,
            "openapi_paths": sorted(schema["paths"]),
        }

    return app
