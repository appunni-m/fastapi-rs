"""Input-only ASGI workload for a mounted FastAPI sub-application."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/app")
    def read_main():
        return {"message": "Hello World from main app"}

    subapi = FastAPI()

    @subapi.get("/sub")
    def read_sub():
        return {"message": "Hello World from sub API"}

    app.mount("/subapi", subapi)
    return app
