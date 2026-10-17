"""Input workload for FastAPI behavior embedded in SQL tutorial headings.

The SQLModel database and transaction paths are replaced by fixed in-memory
records. The workload keeps only the documented FastAPI route signatures,
request validation, response models, and OpenAPI surface under observation.
"""

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


class Hero(BaseModel):
    id: int | None = None
    name: str
    age: int | None = None
    secret_name: str


class HeroPublic(BaseModel):
    id: int
    name: str
    age: int | None = None


def _initial_heroes() -> dict[int, Hero]:
    return {
        1: Hero(id=1, name="Ada", age=37, secret_name="The Analyst"),
        2: Hero(id=2, name="Grace", age=42, secret_name="The Compiler"),
    }


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    """Create a fresh app with one documented SQL tutorial route revision."""
    revision = factory_input["revision"]
    app = FastAPI()
    heroes = _initial_heroes()

    if revision == "single-model":

        @app.get("/heroes/")
        def read_heroes(
            offset: int = 0,
            limit: Annotated[int, Query(le=100)] = 100,
        ) -> list[Hero]:
            values = list(heroes.values())
            return values[offset : offset + limit]

        @app.get("/heroes/{hero_id}")
        def read_hero(hero_id: int) -> Hero:
            hero = heroes.get(hero_id)
            if hero is None:
                raise HTTPException(status_code=404, detail="Hero not found")
            return hero

        @app.delete("/heroes/{hero_id}")
        def delete_hero(hero_id: int):
            if heroes.pop(hero_id, None) is None:
                raise HTTPException(status_code=404, detail="Hero not found")
            return {"ok": True}

        return app

    if revision == "multiple-models":

        @app.get("/heroes/{hero_id}", response_model=HeroPublic)
        def read_hero_with_public_model(hero_id: int):
            hero = heroes.get(hero_id)
            if hero is None:
                raise HTTPException(status_code=404, detail="Hero not found")
            return hero.model_dump()

        @app.delete("/heroes/{hero_id}")
        def delete_hero_again(hero_id: int):
            if heroes.pop(hero_id, None) is None:
                raise HTTPException(status_code=404, detail="Hero not found")
            return {"ok": True}

        return app

    raise ValueError(f"unknown SQL tutorial input revision: {revision!r}")
