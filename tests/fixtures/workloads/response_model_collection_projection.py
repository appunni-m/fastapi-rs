"""Collection-level response-model include and exclude input workload."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Record(BaseModel):
    name: str
    secret: str
    rank: int


class Collection(BaseModel):
    records: list[Record]
    label: str


def create_app() -> FastAPI:
    app = FastAPI(title="Response Model Collection Projection")

    @app.get(
        "/include-all",
        response_model=Collection,
        response_model_include={"records": {"__all__": {"name"}}},
    )
    async def include_fields_for_every_record() -> dict[str, object]:
        return {
            "label": "include-case",
            "records": [
                {"name": "Ada", "secret": "secret-a", "rank": 1},
                {"name": "Lin", "secret": "secret-b", "rank": 2},
            ],
        }

    @app.get(
        "/exclude-all",
        response_model=Collection,
        response_model_exclude={"records": {"__all__": {"secret"}}},
    )
    async def exclude_fields_for_every_record() -> Collection:
        return Collection(
            label="exclude-case",
            records=[
                Record(name="Mira", secret="secret-c", rank=3),
                Record(name="Noor", secret="secret-d", rank=4),
            ],
        )

    return app
