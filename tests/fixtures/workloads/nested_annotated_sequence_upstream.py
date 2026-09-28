"""Independent nested Annotated set query and length constraint route."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import Field

MaxSizedSet = Annotated[set[str], Field(max_length=3)]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def read_root(foo: Annotated[MaxSizedSet | None, Query()] = None) -> dict[str, object]:
        return {"foo": foo}

    return app
