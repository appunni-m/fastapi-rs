"""Input workload for SQL tutorial FastAPI behavior without database libraries."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel


class HeroBase(BaseModel):
    name: str
    age: int | None = None


class HeroCreate(HeroBase):
    secret_name: str


class HeroPublic(HeroBase):
    id: int


def create_app() -> FastAPI:
    app = FastAPI()
    store: dict[str, Any] = {"heroes": [], "next_id": 1}
    cleanup_count = 0

    async def get_session():
        nonlocal cleanup_count
        session = {"store": store}
        try:
            yield session
        finally:
            cleanup_count += 1

    @app.post("/heroes/", response_model=HeroPublic)
    async def create_hero(
        hero: HeroCreate, session: Annotated[dict[str, Any], Depends(get_session)]
    ) -> Any:
        hero_record = {
            "id": session["store"]["next_id"],
            "name": hero.name,
            "age": hero.age,
            "secret_name": hero.secret_name,
        }
        session["store"]["next_id"] += 1
        session["store"]["heroes"].append(hero_record)
        return hero_record

    @app.get("/cleanup-state")
    async def read_cleanup_state() -> dict[str, int]:
        return {"cleanup_count": cleanup_count}

    return app
