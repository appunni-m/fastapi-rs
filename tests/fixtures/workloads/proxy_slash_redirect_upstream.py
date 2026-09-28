"""Input workload for slash redirects under an HTTPS proxy origin."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    def read_items() -> list[str]:
        return ["gear", "map"]

    return app
