from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/atlas/test_path_params_test_tutorial002_test_openapi_schema/items/{item_id}")
    async def read_item(item_id: int):
        return {"item_id": item_id}

    return app
