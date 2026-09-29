from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/app-get", response_description="App GET")
    async def app_get() -> None:
        return None

    @app.put("/app-put", response_description="App PUT")
    async def app_put() -> None:
        return None

    @app.delete("/app-delete", response_description="App DELETE")
    async def app_delete() -> None:
        return None

    @app.patch("/app-patch", response_description="App PATCH")
    async def app_patch() -> None:
        return None

    @app.head("/app-head", response_description="App HEAD")
    async def app_head() -> None:
        return None

    @app.options("/app-options", response_description="App OPTIONS")
    async def app_options() -> None:
        return None

    @app.trace("/app-trace", response_description="App TRACE")
    async def app_trace() -> None:
        return None

    @app.get("/app-default")
    async def app_default() -> None:
        return None

    @app.put("/app-empty", response_description="")
    async def app_empty() -> None:
        return None

    router = APIRouter()

    @router.post("/router-post", response_description="Router POST")
    async def router_post() -> None:
        return None

    @router.get("/router-get", response_description="Router GET")
    async def router_get() -> None:
        return None

    @router.put("/router-put", response_description="Router PUT")
    async def router_put() -> None:
        return None

    @router.delete("/router-delete", response_description="Router DELETE")
    async def router_delete() -> None:
        return None

    @router.patch("/router-patch", response_description="Router PATCH")
    async def router_patch() -> None:
        return None

    @router.head("/router-head", response_description="Router HEAD")
    async def router_head() -> None:
        return None

    @router.options("/router-options", response_description="Router OPTIONS")
    async def router_options() -> None:
        return None

    @router.trace("/router-trace", response_description="Router TRACE")
    async def router_trace() -> None:
        return None

    app.include_router(router)
    return app
