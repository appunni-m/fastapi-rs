"""Independent request workloads for selected cookie, bytes, JSONL, and SQL tutorials."""

from collections.abc import AsyncIterable, Iterable
from typing import Annotated

from fastapi import Cookie, FastAPI, HTTPException, Query
from pydantic import BaseModel


class DataInput(BaseModel):
    description: str
    data: bytes

    model_config = {"val_json_bytes": "base64"}


class DataOutput(BaseModel):
    description: str
    data: bytes

    model_config = {"ser_json_bytes": "base64"}


class DataRoundTrip(BaseModel):
    description: str
    data: bytes

    model_config = {"val_json_bytes": "base64", "ser_json_bytes": "base64"}


class StreamItem(BaseModel):
    name: str
    description: str | None


class HeroCreate(BaseModel):
    name: str
    age: int | None = None
    secret_name: str


class HeroPublic(BaseModel):
    name: str
    age: int | None = None
    id: int


class HeroUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


_STREAM_ITEMS = [
    StreamItem(name="Copper Kite", description="A small wind-powered toy."),
    StreamItem(name="Glass Comet", description="A reusable classroom model."),
    StreamItem(name="Paper Harbor", description="A folded map holder."),
]


def create_app() -> FastAPI:
    app = FastAPI()
    heroes: list[HeroPublic] = []
    next_hero_id = 1

    @app.get("/items/")
    def cookie_default(ads_id: str | None = Cookie(default=None)):
        return {"ads_id": ads_id}

    @app.get("/items-annotated/")
    def cookie_annotated(ads_id: Annotated[str | None, Cookie()] = None):
        return {"ads_id": ads_id}

    @app.post("/data")
    def decode_data(body: DataInput):
        return {"description": body.description, "content": body.data.decode("utf-8")}

    @app.get("/data")
    def encode_data() -> DataOutput:
        return DataOutput(description="A sample device", data=b"hello")

    @app.post("/data-in-out")
    def round_trip(body: DataRoundTrip) -> DataRoundTrip:
        return body

    @app.get("/items/stream")
    async def stream_async_typed() -> AsyncIterable[StreamItem]:
        for item in _STREAM_ITEMS:
            yield item

    @app.get("/items/stream-no-async")
    def stream_sync_typed() -> Iterable[StreamItem]:
        yield from _STREAM_ITEMS

    @app.get("/items/stream-no-annotation")
    async def stream_async_untyped():
        for item in _STREAM_ITEMS:
            yield item

    @app.get("/items/stream-no-async-no-annotation")
    def stream_sync_untyped():
        yield from _STREAM_ITEMS

    @app.post("/heroes/", response_model=HeroPublic)
    def create_hero(hero: HeroCreate) -> HeroPublic:
        nonlocal next_hero_id
        created = HeroPublic(
            id=next_hero_id,
            name=hero.name,
            age=hero.age,
        )
        next_hero_id += 1
        heroes.append(created)
        return created

    @app.get("/heroes/", response_model=list[HeroPublic])
    def list_heroes(offset: int = 0, limit: int = Query(default=100, le=100)):
        return heroes[offset : offset + limit]

    @app.get("/heroes/{hero_id}", response_model=HeroPublic)
    def read_hero(hero_id: int) -> HeroPublic:
        for hero in heroes:
            if hero.id == hero_id:
                return hero
        raise HTTPException(status_code=404, detail="Hero not found")

    @app.patch("/heroes/{hero_id}", response_model=HeroPublic)
    def update_hero(hero_id: int, patch: HeroUpdate) -> HeroPublic:
        for index, hero in enumerate(heroes):
            if hero.id == hero_id:
                updated = hero.model_copy(update=patch.model_dump(exclude_unset=True))
                heroes[index] = updated
                return updated
        raise HTTPException(status_code=404, detail="Hero not found")

    @app.delete("/heroes/{hero_id}")
    def delete_hero(hero_id: int):
        for index, hero in enumerate(heroes):
            if hero.id == hero_id:
                del heroes[index]
                return {"ok": True}
        raise HTTPException(status_code=404, detail="Hero not found")

    return app
