"""Independent ASGI input for router deprecation and schema inclusion policy."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    router_hidden = APIRouter(include_in_schema=False)

    @router_hidden.get("/router-hidden")
    def read_router_hidden():
        return {"route": "router-hidden"}

    app.include_router(router_hidden, prefix="/api")

    include_hidden = APIRouter()

    @include_hidden.get("/include-hidden")
    def read_include_hidden():
        return {"route": "include-hidden"}

    app.include_router(include_hidden, prefix="/api", include_in_schema=False)

    router_deprecated = APIRouter(deprecated=True)

    @router_deprecated.get("/router-old")
    def read_router_old():
        return {"route": "router-old"}

    app.include_router(router_deprecated, prefix="/api")

    include_deprecated = APIRouter()

    @include_deprecated.get("/include-old")
    def read_include_old():
        return {"route": "include-old"}

    app.include_router(include_deprecated, prefix="/api", deprecated=True)

    router_current = APIRouter(deprecated=False)

    @router_current.get("/current")
    def read_current():
        return {"route": "current"}

    app.include_router(router_current, prefix="/api", deprecated=False)

    nested_parent = APIRouter()
    nested_hidden = APIRouter()

    @nested_hidden.get("/hidden")
    def read_nested_hidden():
        return {"route": "nested-hidden"}

    nested_parent.include_router(
        nested_hidden,
        prefix="/child",
        include_in_schema=False,
    )

    nested_deprecated = APIRouter()

    @nested_deprecated.get("/old")
    def read_nested_old():
        return {"route": "nested-old"}

    nested_parent.include_router(
        nested_deprecated,
        prefix="/child",
        deprecated=True,
    )
    app.include_router(nested_parent, prefix="/api")

    return app
