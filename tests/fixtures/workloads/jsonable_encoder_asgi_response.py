"""Independent ASGI input for FastAPI's no-response-model date encoding path."""

from datetime import date

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/today", response_model=None)
    def today():
        return date(2032, 4, 5)

    return app
