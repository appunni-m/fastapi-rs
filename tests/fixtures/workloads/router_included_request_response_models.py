"""Input workload for request and response models on a nested included route."""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class CreateRecord(BaseModel):
    name: str


class PublicRecord(BaseModel):
    record_id: int
    name: str


def create_app() -> FastAPI:
    leaf_router = APIRouter()

    @leaf_router.post("/records", response_model=PublicRecord)
    def create_record(record: CreateRecord) -> dict[str, object]:
        return {
            "record_id": 41,
            "name": record.name,
            "private_note": "filtered by the response model",
        }

    parent_router = APIRouter()
    parent_router.include_router(leaf_router, prefix="/items")

    app = FastAPI()
    app.include_router(parent_router, prefix="/v1")
    return app
