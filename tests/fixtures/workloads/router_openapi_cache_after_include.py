"""Inputs for checking OpenAPI refresh after a child router gains a route."""

from fastapi import APIRouter, FastAPI


def read_later() -> dict[str, bool]:
    return {"later": True}


def create_app() -> FastAPI:
    router = APIRouter()
    app = FastAPI()
    app.include_router(router, prefix="/api")

    @app.get("/_register-later", include_in_schema=False)
    def register_later() -> dict[str, bool]:
        router.get("/later")(read_later)
        return {"registered": True}

    return app
