from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/atlas/test_path_operation_advanced_configurations_test_tutorial003_test_openapi_schema/items/",
        include_in_schema=False,
    )
    async def read_record():
        return {"record": "copper"}

    return app
