"""An invalid inferred response field rejected during route registration."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.responses import Response


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/invalid-return-field")
    def read_archive() -> Response | None:
        return Response(content="independent archive representation")

    return app
