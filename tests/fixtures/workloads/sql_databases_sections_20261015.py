"""FastAPI request and schema inputs for SQL tutorial examples.

The SQLModel and SQLAlchemy implementation is intentionally represented by
ordinary Pydantic models and an in-memory record. These inputs exercise the
FastAPI request, response, and OpenAPI boundary without claiming database
engine, transaction, or persistence behavior.
"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class Hero(BaseModel):
    id: int | None = None
    name: str
    age: int | None = None
    secret_name: str


class HeroBase(BaseModel):
    name: str
    age: int | None = None


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    """Build one documented model variant for an independently isolated case."""
    revision = factory_input["revision"]
    app = FastAPI()

    if revision == "single-model":

        @app.post("/heroes/")
        def create_hero(hero: Hero) -> Hero:
            return hero

        return app

    if revision == "multiple-models":

        @app.post("/heroes/", response_model=HeroPublic)
        def create_hero(hero: HeroCreate) -> dict[str, Any]:
            return {"id": 1, **hero.model_dump()}

        @app.get("/heroes/", response_model=list[HeroPublic])
        def read_heroes() -> list[dict[str, Any]]:
            return [
                {
                    "id": 1,
                    "name": "Ada",
                    "age": 37,
                    "secret_name": "The Analyst",
                }
            ]

        @app.patch("/heroes/{hero_id}", response_model=HeroPublic)
        def update_hero(hero_id: int, hero: HeroUpdate) -> dict[str, Any]:
            record = {
                "id": hero_id,
                "name": "Ada",
                "age": 37,
                "secret_name": "The Analyst",
            }
            record.update(hero.model_dump(exclude_unset=True))
            return record

        return app

    raise ValueError(f"unknown SQL tutorial input revision: {revision!r}")
