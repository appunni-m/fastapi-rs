"""Input-only ASGI workload for the synchronous first-steps tutorial."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    return app
