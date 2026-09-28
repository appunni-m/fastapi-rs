"""Independent ASGI inputs for conditional OpenAPI and docs registration."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Conditional Interface Probe", version="3.7")

    @app.get("/")
    def landing():
        return {"message": "Independent landing response"}

    hidden = FastAPI(
        title="Hidden Interface Probe",
        version="3.7",
        openapi_url="",
    )
    app.mount("/hidden", hidden)
    return app
