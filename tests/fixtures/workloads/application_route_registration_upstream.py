"""Independent workload for FastAPI route-registration entry points."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.api_route("/api_route")
    def api_route_endpoint():
        return {"message": "Hello World"}

    def add_api_route_endpoint():
        return {"message": "Hello World"}

    app.add_api_route("/non_decorated_route", add_api_route_endpoint)

    return app
