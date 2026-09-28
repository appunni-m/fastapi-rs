from fastapi import FastAPI
from pydantic import BaseModel


class AtlasRecord(BaseModel):
    title: str
    price: float
    description: str | None = None
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/atlas/test_path_operation_configurations_test_tutorial001_test_openapi_schema/items/",
        status_code=201,
    )
    async def create_record(record: AtlasRecord) -> AtlasRecord:
        return record

    return app
