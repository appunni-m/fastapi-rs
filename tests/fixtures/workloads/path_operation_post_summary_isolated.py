from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", summary="Create an item")
    async def create_item() -> None:
        return None

    return app
