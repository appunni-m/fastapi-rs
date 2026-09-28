"""Independent repeated-query input workload for integer-list validation."""

from __future__ import annotations

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/readings")
    def read_readings(q: list[int] = Query(default=None)) -> dict[str, list[int] | None]:  # noqa: B008
        return {"q": q}

    return app
