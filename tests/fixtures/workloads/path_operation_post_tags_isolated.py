from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", tags=["items"])
    async def create_item() -> None:
        return None

    return app
