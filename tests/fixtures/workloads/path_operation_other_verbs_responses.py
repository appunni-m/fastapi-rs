from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/app-get", responses={418: {"description": "App GET tea"}, 501: {"description": "App GET"}}
    )
    async def app_get() -> None:
        return None

    @app.post(
        "/app-post",
        responses={418: {"description": "App POST tea"}, 501: {"description": "App POST"}},
    )
    async def app_post() -> None:
        return None

    @app.put(
        "/app-put", responses={418: {"description": "App PUT tea"}, 501: {"description": "App PUT"}}
    )
    async def app_put() -> None:
        return None

    @app.delete(
        "/app-delete",
        responses={418: {"description": "App DELETE tea"}, 501: {"description": "App DELETE"}},
    )
    async def app_delete() -> None:
        return None

    @app.patch(
        "/app-patch",
        responses={418: {"description": "App PATCH tea"}, 501: {"description": "App PATCH"}},
    )
    async def app_patch() -> None:
        return None

    @app.head(
        "/app-head",
        responses={418: {"description": "App HEAD tea"}, 501: {"description": "App HEAD"}},
    )
    async def app_head() -> None:
        return None

    @app.options(
        "/app-options",
        responses={418: {"description": "App OPTIONS tea"}, 501: {"description": "App OPTIONS"}},
    )
    async def app_options() -> None:
        return None

    @app.trace(
        "/app-trace",
        responses={418: {"description": "App TRACE tea"}, 501: {"description": "App TRACE"}},
    )
    async def app_trace() -> None:
        return None

    router = APIRouter()

    @router.get(
        "/router-get",
        responses={418: {"description": "Router GET tea"}, 501: {"description": "Router GET"}},
    )
    async def router_get() -> None:
        return None

    @router.post(
        "/router-post",
        responses={418: {"description": "Router POST tea"}, 501: {"description": "Router POST"}},
    )
    async def router_post() -> None:
        return None

    @router.put(
        "/router-put",
        responses={418: {"description": "Router PUT tea"}, 501: {"description": "Router PUT"}},
    )
    async def router_put() -> None:
        return None

    @router.delete(
        "/router-delete",
        responses={
            418: {"description": "Router DELETE tea"},
            501: {"description": "Router DELETE"},
        },
    )
    async def router_delete() -> None:
        return None

    @router.patch(
        "/router-patch",
        responses={418: {"description": "Router PATCH tea"}, 501: {"description": "Router PATCH"}},
    )
    async def router_patch() -> None:
        return None

    @router.head(
        "/router-head",
        responses={418: {"description": "Router HEAD tea"}, 501: {"description": "Router HEAD"}},
    )
    async def router_head() -> None:
        return None

    @router.options(
        "/router-options",
        responses={
            418: {"description": "Router OPTIONS tea"},
            501: {"description": "Router OPTIONS"},
        },
    )
    async def router_options() -> None:
        return None

    @router.trace(
        "/router-trace",
        responses={418: {"description": "Router TRACE tea"}, 501: {"description": "Router TRACE"}},
    )
    async def router_trace() -> None:
        return None

    app.include_router(router)
    return app
