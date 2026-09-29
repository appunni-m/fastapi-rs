"""Focused input workload for FastAPI OPTIONS and TRACE route decorators."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.options("/verbs")
    def options_route():
        return {"method": "OPTIONS"}

    @app.trace("/verbs")
    def trace_route():
        return {"method": "TRACE"}

    return app
