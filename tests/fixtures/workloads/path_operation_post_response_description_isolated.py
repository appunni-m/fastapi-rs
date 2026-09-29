from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items", response_description="The created item")
    async def create_item() -> None:
        return None

    @app.post("/items-default")
    async def default_description() -> None:
        return None

    @app.post("/items-empty", response_description="")
    async def empty_description() -> None:
        return None

    return app
