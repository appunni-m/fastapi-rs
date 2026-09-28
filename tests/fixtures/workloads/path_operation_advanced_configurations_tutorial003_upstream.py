from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/", include_in_schema=False)
    async def read_items():
        return [{"item_id": "Foo"}]

    return app
