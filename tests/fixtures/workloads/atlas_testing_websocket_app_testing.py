"""Input-only ASGI workload for the FastAPI app-testing tutorial routes."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def read_main():
        return {"msg": "Hello World"}

    return app
