"""Independent Pydantic request-model validation workload."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import Body, Cookie, FastAPI, Header, Query
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None
    tags: list[str] = Field(default_factory=list)
    image: Image | None = None


class User(BaseModel):
    username: str
    display_name: str | None = None


class Metric(BaseModel):
    label: str
    amount: int


class NameChoice(BaseModel):
    name: str | None = None


class PriceChoice(BaseModel):
    price: int


class Cat(BaseModel):
    kind: Literal["cat"]
    meows: int


class Dog(BaseModel):
    kind: Literal["dog"]
    barks: float


Pet = Annotated[Cat | Dog, Field(discriminator="kind")]


class BaseRecord(BaseModel):
    name: str | None = None


class DetailedRecord(BaseRecord):
    revision: int


class QueryFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=100, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = Field(default_factory=list)


class CookieSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


class HeaderSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = Field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/{item_id}")
    async def update_item(item_id: int, item: Item, user: User) -> dict[str, object]:
        return {"item_id": item_id, "item": item, "user": user}

    @app.post("/metrics")
    async def create_metrics(metrics: list[Metric]) -> dict[str, list[Metric]]:
        return {"metrics": metrics}

    @app.post("/choices")
    async def choose_variant(item: PriceChoice | NameChoice) -> dict[str, object]:
        return {"item": item}

    @app.post("/pets")
    async def create_pet(pet: Annotated[Pet, Body()]) -> Pet:
        return pet

    @app.post("/records")
    async def create_record(record: DetailedRecord | BaseRecord) -> dict[str, object]:
        return {"record": record}

    @app.post("/priority-items")
    async def create_priority_item(item: Item, priority: int) -> dict[str, object]:
        return {"item": item, "priority": priority}

    @app.post("/embedded-items")
    async def create_embedded_item(item: Annotated[Item, Body(embed=True)]) -> dict[str, Item]:
        return {"item": item}

    @app.put("/catalog/{catalog_id}")
    async def update_catalog(catalog_id: int, item: Item) -> dict[str, object]:
        return {"catalog_id": catalog_id, "item": item}

    @app.post("/image-groups")
    async def create_image_group(images: list[Image]) -> dict[str, list[Image]]:
        return {"images": images}

    @app.get("/filters")
    async def read_filters(filters: Annotated[QueryFilters, Query()]) -> QueryFilters:
        return filters

    @app.get("/session")
    async def read_session(settings: Annotated[CookieSettings, Cookie()]) -> CookieSettings:
        return settings

    @app.get("/trace")
    async def read_trace(settings: Annotated[HeaderSettings, Header()]) -> HeaderSettings:
        return settings

    @app.get("/trace-literal")
    async def read_trace_literal(
        settings: Annotated[HeaderSettings, Header(convert_underscores=False)],
    ) -> HeaderSettings:
        return settings

    return app
