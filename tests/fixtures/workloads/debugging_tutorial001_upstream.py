"""ASGI workload for the FastAPI-owned debugging tutorial route."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def root() -> dict[str, str]:
        first = "a"
        second = "b" + first
        return {"hello world": second}

    return app
