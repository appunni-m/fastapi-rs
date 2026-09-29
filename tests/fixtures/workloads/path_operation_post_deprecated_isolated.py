from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items")
    async def create_item() -> None:
        return None

    @app.post("/items-deprecated", deprecated=True)
    async def create_deprecated_item() -> None:
        return None

    return app
