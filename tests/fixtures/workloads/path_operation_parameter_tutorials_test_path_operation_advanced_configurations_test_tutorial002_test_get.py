from fastapi import FastAPI
from fastapi.routing import APIRoute


def atlas_unique_id(route: APIRoute) -> str:
    return "atlas_" + route.name


def create_app() -> FastAPI:
    app = FastAPI(generate_unique_id_function=atlas_unique_id)

    @app.get("/atlas/test_path_operation_advanced_configurations_test_tutorial002_test_get/items/")
    async def read_record():
        return {"record": "copper"}

    return app
