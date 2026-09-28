"""ASGI workload for built-in generic request and response annotations."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/list/", response_model=list[int])
    def list_endpoint(input: list[int]) -> list[int]:
        return input

    @app.post("/mapping/", response_model=dict[str, list[int]])
    def mapping_endpoint(input: dict[str, list[int]]) -> dict[str, list[int]]:
        return input

    @app.post("/set/", response_model=set[int])
    def set_endpoint(input: set[int]) -> set[int]:
        return input

    @app.post("/tuple/", response_model=tuple[int, ...])
    def tuple_endpoint(input: tuple[int, ...]) -> tuple[int, ...]:
        return input

    return app
