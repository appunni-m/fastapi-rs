from enum import Enum

from fastapi import FastAPI


class Tags(Enum):
    items = "items"
    users = "users"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/", tags=[Tags.items])
    async def get_items():
        return ["Portal gun", "Plumbus"]

    @app.get("/users/", tags=[Tags.users])
    async def read_users():
        return ["Rick", "Morty"]

    return app
