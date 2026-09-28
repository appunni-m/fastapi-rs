from fastapi import FastAPI
from pydantic import BaseModel


class AtlasRecord(BaseModel):
    title: str
    price: float
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/atlas/test_path_operation_configurations_test_tutorial002_test_openapi_schema/items/",
        tags=["assets"],
    )
    async def create_record(record: AtlasRecord) -> AtlasRecord:
        return record

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial002_test_openapi_schema/items/",
        tags=["assets"],
    )
    async def read_assets():
        return [{"title": "cedar", "price": 17}]

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial002_test_openapi_schema/users/",
        tags=["operators"],
    )
    async def read_operators():
        return [{"handle": "mira"}]

    return app
