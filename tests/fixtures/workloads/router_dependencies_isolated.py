from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Query


def create_app() -> FastAPI:
    events: list[str] = []

    def router_dependency(token: Annotated[str, Query()]):
        events.append(f"router:{token}")

    def include_dependency(scope: Annotated[str, Query()]):
        events.append(f"include:{scope}")

    router = APIRouter(dependencies=[Depends(router_dependency)])

    @router.get("/items")
    def read_items():
        return {"events": events}

    app = FastAPI()
    app.include_router(router, dependencies=[Depends(include_dependency)])
    return app
