"""Independent dispatch input for FastAPI's inherited add_route API."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()

    def read_record(request):
        return PlainTextResponse(f"compat:{request.path_params['record_id']}")

    app.add_route(
        "/compat-records/{record_id}",
        read_record,
        methods=["GET"],
        name="compat-record",
        include_in_schema=False,
    )
    return app
