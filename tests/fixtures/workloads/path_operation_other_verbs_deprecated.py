from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/app-put", deprecated=True)
    async def app_put() -> None:
        return None

    @app.delete("/app-delete", deprecated=True)
    async def app_delete() -> None:
        return None

    @app.patch("/app-patch", deprecated=True)
    async def app_patch() -> None:
        return None

    @app.head("/app-head", deprecated=True)
    async def app_head() -> None:
        return None

    @app.options("/app-options", deprecated=True)
    async def app_options() -> None:
        return None

    @app.trace("/app-trace", deprecated=True)
    async def app_trace() -> None:
        return None

    @app.put("/app-put-false", deprecated=False)
    async def app_put_false() -> None:
        return None

    @app.put("/app-put-default")
    async def app_put_default() -> None:
        return None

    router = APIRouter()

    @router.put("/router-put", deprecated=True)
    async def router_put() -> None:
        return None

    @router.delete("/router-delete", deprecated=True)
    async def router_delete() -> None:
        return None

    @router.patch("/router-patch", deprecated=True)
    async def router_patch() -> None:
        return None

    @router.head("/router-head", deprecated=True)
    async def router_head() -> None:
        return None

    @router.options("/router-options", deprecated=True)
    async def router_options() -> None:
        return None

    @router.trace("/router-trace", deprecated=True)
    async def router_trace() -> None:
        return None

    @router.put("/router-put-false", deprecated=False)
    async def router_put_false() -> None:
        return None

    @router.put("/router-put-default")
    async def router_put_default() -> None:
        return None

    app.include_router(router)
    return app
