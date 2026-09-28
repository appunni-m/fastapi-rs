from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/atlas/test_path_operation_advanced_configurations_test_tutorial001_test_get/items/",
        operation_id="atlas_custom_operation_1_test_get",
    )
    async def read_record():
        return {"record": "copper"}

    return app
