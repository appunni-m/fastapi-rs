"""Independent single-route workload for response-validation errors."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class User(BaseModel):
    name: str
    surname: str


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/invalid-output", response_model=User)
    def invalid_output():
        return {"name": "John"}

    return app
