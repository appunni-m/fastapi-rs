from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/sync")
    def sync_handler() -> dict[str, str]:
        return {"handler": "sync"}

    @app.get("/async")
    async def async_handler() -> dict[str, str]:
        return {"handler": "async"}

    return app
