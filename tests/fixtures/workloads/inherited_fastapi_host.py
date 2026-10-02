"""Independent Host-route dispatch input for FastAPI's inherited host API."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Router


def create_app() -> FastAPI:
    app = FastAPI()

    def read_record(request):
        tenant = request.path_params["tenant"]
        record_id = request.path_params["record_id"]
        return PlainTextResponse(f"{tenant}:{record_id}")

    records = Router(routes=[Route("/records/{record_id}", read_record, name="record")])
    app.host("{tenant}.records.example", records, name="records")
    return app
