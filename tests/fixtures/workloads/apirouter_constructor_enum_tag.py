"""String-valued Enum tags supplied to the APIRouter constructor."""

from enum import Enum
from typing import Any

from fastapi import APIRouter, FastAPI


class OperationTags(Enum):
    items = "enum-items"


def create_app(_factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    router = APIRouter(tags=[OperationTags.items])

    @router.get("/items")
    def read_items():
        return {"items": ["pen", "notebook"]}

    app = FastAPI()
    app.include_router(router)
    return app
