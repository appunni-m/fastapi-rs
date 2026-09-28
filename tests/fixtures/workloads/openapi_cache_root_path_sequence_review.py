"""Independent app for repeated root-path OpenAPI requests followed by a clean request."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def root() -> dict[str, bool]:
        return {"ready": True}

    return app
