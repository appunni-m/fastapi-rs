"""Two GET handlers registered for the same users path."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/users")
    async def read_users():
        return ["Rick", "Morty"]

    @app.get("/users")
    async def read_users2():
        return ["Bean", "Elfo"]

    return app
