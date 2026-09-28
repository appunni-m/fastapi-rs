"""Independent route input for the configured tutorial response status."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", status_code=201)
    async def create_item(name: str):
        return {"name": name}

    return app
