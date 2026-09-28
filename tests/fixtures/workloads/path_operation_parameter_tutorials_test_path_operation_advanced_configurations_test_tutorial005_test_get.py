from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/atlas/test_path_operation_advanced_configurations_test_tutorial005_test_get/items/",
        openapi_extra={"x-atlas-review-marker": "ember"},
    )
    async def read_record():
        return {"record": "portal"}

    return app
