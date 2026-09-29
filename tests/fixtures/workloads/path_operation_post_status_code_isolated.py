from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items-default")
    async def create_item_default() -> None:
        return None

    @app.post("/items-created", status_code=201)
    async def create_item() -> None:
        return None

    return app
