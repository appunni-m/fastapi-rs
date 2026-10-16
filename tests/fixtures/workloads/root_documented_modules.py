"""Expose documented FastAPI root module attributes for parity observation."""

import fastapi
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/root-modules")
    def root_modules() -> dict[str, bool]:
        names = (
            "datastructures",
            "encoders",
            "exception_handlers",
            "middleware",
            "openapi",
            "requests",
            "responses",
            "routing",
            "security",
            "sse",
            "websockets",
        )
        return {name: hasattr(fastapi, name) for name in names}

    return app
