"""Independent minimal app for bodyless OpenAPI response metadata."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/empty", status_code=204)
    def empty_response() -> None:
        return None

    @app.get("/b", responses={204: {"description": "No Content"}})
    async def explicit_204_response():
        return None

    return app
