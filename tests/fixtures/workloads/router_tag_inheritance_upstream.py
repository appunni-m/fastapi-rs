"""Independent ASGI stimulus for ordered tag inheritance across router includes."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    parent = APIRouter(tags=["parent"])
    child = APIRouter(prefix="/items", tags=["router"])

    @child.get("/{item_id}", tags=["route"])
    def read_item(item_id: int):
        return {"item_id": item_id}

    parent.include_router(child, prefix="/v1", tags=["include"])
    app.include_router(parent, prefix="/api", tags=["app"])
    return app
