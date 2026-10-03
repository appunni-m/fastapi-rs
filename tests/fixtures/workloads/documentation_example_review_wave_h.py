"""Independent runtime inputs for pending FastAPI documentation examples."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    WebSocket,
)
from fastapi.routing import APIRoute


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable[..., Any]:
        original = super().get_route_handler()

        async def handle(request: Request) -> Response:
            response = await original(request)
            response.headers["X-Response-Time"] = "0"
            return response

        return handle


async def _query_token(token: str = Query()) -> None:
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def _header_token(x_token: Annotated[str, Header()]) -> None:
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one small FastAPI app selected by an input-only recipe case."""
    del event_trace
    scenario = factory_input["scenario"]

    if scenario == "proxy-items":
        app = FastAPI()

        @app.get("/items/")
        async def read_items() -> list[str]:
            return ["plumbus", "portal gun"]

        return app

    if scenario == "bigger-applications":
        app = FastAPI(dependencies=[Depends(_query_token)])
        users = APIRouter(tags=["users"])
        items = APIRouter(
            prefix="/items",
            tags=["items"],
            dependencies=[Depends(_header_token)],
            responses={404: {"description": "Not found"}},
        )
        admin = APIRouter(
            tags=["admin"],
            dependencies=[Depends(_header_token)],
            responses={418: {"description": "I'm a teapot"}},
        )

        @users.get("/users/me")
        async def read_user_me() -> dict[str, str]:
            return {"username": "sample-user"}

        @items.get("/{item_id}")
        async def read_item(item_id: str) -> dict[str, str]:
            if item_id != "plumbus":
                raise HTTPException(status_code=404, detail="Item not found")
            return {"item_id": item_id, "name": "Plumbus"}

        @admin.post("/")
        async def update_admin() -> dict[str, str]:
            return {"message": "Admin route accepted"}

        app.include_router(users)
        app.include_router(items)
        app.include_router(admin, prefix="/admin", tags=["admin"])
        return app

    if scenario == "class-dependency":
        app = FastAPI()
        rows = [{"item_name": "Oak"}, {"item_name": "Elm"}, {"item_name": "Ash"}]

        @app.get("/items/class")
        async def class_dependency(
            commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
        ) -> dict[str, Any]:
            result: dict[str, Any] = {"items": rows[commons.skip : commons.skip + commons.limit]}
            if commons.q:
                result["q"] = commons.q
            return result

        @app.get("/items/inferred")
        async def inferred_dependency(
            commons: Annotated[CommonQueryParams, Depends()],
        ) -> dict[str, Any]:
            result: dict[str, Any] = {"items": rows[commons.skip : commons.skip + commons.limit]}
            if commons.q:
                result["q"] = commons.q
            return result

        return app

    if scenario in {"settings-direct", "settings-dependency"}:
        app = FastAPI()
        settings = {
            "app_name": "Independent API",
            "admin_email": "admin@example.invalid",
            "items_per_user": 17,
        }

        def get_settings() -> dict[str, Any]:
            return settings

        if scenario == "settings-direct":

            @app.get("/info")
            async def info() -> dict[str, Any]:
                return settings

        else:

            @app.get("/info")
            async def info(
                current_settings: Annotated[dict[str, Any], Depends(get_settings)],
            ) -> dict[str, Any]:
                return current_settings

        return app

    if scenario == "timed-route":
        app = FastAPI()
        router = APIRouter(route_class=TimedRoute)

        @app.get("/")
        async def ordinary() -> dict[str, str]:
            return {"message": "ordinary route"}

        @router.get("/timed")
        async def timed() -> dict[str, str]:
            return {"message": "timed route"}

        app.include_router(router)
        return app

    if scenario == "websocket-echo":
        app = FastAPI()

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            while True:
                try:
                    data = await websocket.receive_text()
                except Exception:
                    return
                await websocket.send_text(f"Message text was: {data}")

        return app

    if scenario == "frontend-explicit-404":
        app = FastAPI()
        directory = TemporaryDirectory(prefix="fastapi-wave-h-frontend-")
        Path(directory.name, "404.html").write_text("custom not found", encoding="utf-8")
        app.state.documentation_example_wave_h_directories = [directory]
        app.frontend("/", directory=directory.name, fallback="404.html")
        return app

    raise ValueError(f"unsupported documentation example scenario: {scenario}")
