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
        "/atlas/test_path_operation_configurations_test_tutorial005_test_query_params_str_validations/items/",
        summary="Create a ledger entry",
        response_description="The accepted ledger record",
    )
    async def create_record(record: AtlasRecord) -> AtlasRecord:
        return record

    return app
