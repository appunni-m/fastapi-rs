from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/app-get", status_code=None)
    async def app_get() -> None:
        return None

    @app.post("/app-post", status_code=None)
    async def app_post() -> None:
        return None

    @app.put("/app-put", status_code=None)
    async def app_put() -> None:
        return None

    @app.delete("/app-delete", status_code=None)
    async def app_delete() -> None:
        return None

    @app.patch("/app-patch", status_code=None)
    async def app_patch() -> None:
        return None

    @app.head("/app-head", status_code=None)
    async def app_head() -> None:
        return None

    @app.options("/app-options", status_code=None)
    async def app_options() -> None:
        return None

    @app.trace("/app-trace", status_code=None)
    async def app_trace() -> None:
        return None

    router = APIRouter()

    @router.get("/router-get", status_code=None)
    async def router_get() -> None:
        return None

    @router.post("/router-post", status_code=None)
    async def router_post() -> None:
        return None

    @router.put("/router-put", status_code=None)
    async def router_put() -> None:
        return None

    @router.delete("/router-delete", status_code=None)
    async def router_delete() -> None:
        return None

    @router.patch("/router-patch", status_code=None)
    async def router_patch() -> None:
        return None

    @router.head("/router-head", status_code=None)
    async def router_head() -> None:
        return None

    @router.options("/router-options", status_code=None)
    async def router_options() -> None:
        return None

    @router.trace("/router-trace", status_code=None)
    async def router_trace() -> None:
        return None

    app.include_router(router)
    return app
