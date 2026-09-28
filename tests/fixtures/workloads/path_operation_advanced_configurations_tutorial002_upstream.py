from fastapi import FastAPI
from fastapi.routing import APIRoute


def create_app() -> FastAPI:
    def generate_unique_id(route: APIRoute) -> str:
        return route.name

    app = FastAPI(generate_unique_id_function=generate_unique_id)

    @app.get("/items/")
    async def read_items():
        return [{"item_id": "Foo"}]

    return app
