"""Isolated response status-key inputs from FastAPI's additional-response test."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/response-ranges",
        responses={
            "400": {"description": "Error with str"},
            "5xx": {"description": "Error with range, lower"},
            "default": {"description": "A default response"},
        },
    )
    async def response_ranges():
        return "range inputs"

    return app
