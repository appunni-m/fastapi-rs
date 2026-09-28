"""Exercise request models on same-named endpoints included from two routers."""

from __future__ import annotations

from fastapi import APIRouter, Body, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    north_router = APIRouter()
    south_router = APIRouter()

    def north_calculate(units: int = Body(), label: str = Body()) -> dict[str, object]:
        return {"units": units, "label": label}

    north_calculate.__name__ = "calculate"
    north_router.post("/calculate")(north_calculate)

    def south_calculate(units: int = Body(), label: str = Body()) -> dict[str, object]:
        return {"units": units, "label": label}

    south_calculate.__name__ = "calculate"
    south_router.post("/calculate/")(south_calculate)

    app.include_router(north_router, prefix="/north")
    app.include_router(south_router, prefix="/south")
    return app
