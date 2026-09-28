"""Independent ASGI stimuli for Starlette StaticFiles behavior."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")
    return app
