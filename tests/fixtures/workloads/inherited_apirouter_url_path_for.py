"""Independent nested-router URL-reversal input for APIRouter's inherited API."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from starlette.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()
    entries = APIRouter()

    @entries.get("/entries/{entry_id}", name="entry")
    def read_entry(entry_id: str):
        return {"entry_id": entry_id}

    parent = APIRouter()
    parent.include_router(entries, prefix="/north")
    parent.include_router(entries, prefix="/south")
    app.include_router(parent)

    @app.get("/_probe/router-path")
    def router_path():
        return PlainTextResponse(str(parent.url_path_for("entry", entry_id="E-814")))

    return app
