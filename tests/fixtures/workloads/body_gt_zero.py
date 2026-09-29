"""Focused scalar-body constraint workload adapted from FastAPI's tutorial."""

from typing import Annotated

from fastapi import Body, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/importance")
    def submit_importance(importance: int = Body(gt=0)):
        return {"importance": importance}

    @app.post("/annotated-importance")
    def submit_annotated_importance(importance: Annotated[int, Body(gt=0)]):
        return {"importance": importance}

    return app
