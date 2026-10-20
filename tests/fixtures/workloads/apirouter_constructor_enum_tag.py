"""String-valued Enum tags supplied to the APIRouter constructor."""

from enum import Enum
from typing import Any

from fastapi import APIRouter, FastAPI


class OperationTags(Enum):
    items = "enum-items"


def create_app(_factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    default_router = APIRouter()
    _event_trace.append(f"default:{type(default_router.tags).__name__}:{default_router.tags!r}")

    empty_tags = []
    empty_router = APIRouter(tags=empty_tags)
    _event_trace.append(f"empty:{empty_router.tags is empty_tags}:{empty_router.tags!r}")

    tags = [OperationTags.items]
    router = APIRouter(tags=tags)
    _event_trace.append(f"enum:{type(router.tags).__name__}:{router.tags is tags}:{router.tags!r}")

    @router.get("/items")
    def read_items():
        return {"items": ["pen", "notebook"]}

    app = FastAPI()
    app.include_router(router)
    return app
