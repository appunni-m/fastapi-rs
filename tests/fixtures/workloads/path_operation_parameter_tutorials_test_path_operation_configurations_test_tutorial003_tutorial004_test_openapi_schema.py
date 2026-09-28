from fastapi import FastAPI
from pydantic import BaseModel


class AtlasRecord(BaseModel):
    title: str
    price: float
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/atlas/test_path_operation_configurations_test_tutorial003_tutorial004_test_openapi_schema/items/compact",
        summary="Create a ledger entry",
    )
    async def create_compact(record: AtlasRecord) -> AtlasRecord:
        """A short independently authored summary."""
        return record

    @app.post(
        "/atlas/test_path_operation_configurations_test_tutorial003_tutorial004_test_openapi_schema/items/detailed",
        summary="Create a ledger entry",
    )
    async def create_detailed(record: AtlasRecord) -> AtlasRecord:
        """Create a ledger entry with its required title and price.

        The second route exercises a multiline endpoint docstring description.
        """
        return record

    return app
