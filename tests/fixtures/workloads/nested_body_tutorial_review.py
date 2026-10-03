"""Independent nested request-body probes for the body tutorial review."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl


class TypedTagEntry(BaseModel):
    name: str
    score: float
    tags: list[str] = Field(default_factory=list)


class BareTagEntry(BaseModel):
    name: str
    price: float
    tags: list = []


class UniqueTagEntry(BaseModel):
    name: str
    score: float
    tags: set[str] = Field(default_factory=set)


class ReviewImage(BaseModel):
    href: HttpUrl
    caption: str


class ReviewAsset(BaseModel):
    name: str
    cost: float
    image: ReviewImage | None = None
    images: list[ReviewImage] | None = None


class OfferLine(BaseModel):
    name: str
    cost: float
    labels: set[str] = Field(default_factory=set)
    images: list[ReviewImage] | None = None


class ReviewOffer(BaseModel):
    name: str
    cost: float
    lines: list[OfferLine]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/tag-forms/typed/{entry_id}")
    async def replace_typed_tags(entry_id: int, entry: TypedTagEntry):
        return {"entry_id": entry_id, "entry": entry}

    @app.put("/tag-forms/bare/{entry_id}")
    async def replace_bare_tags(entry_id: int, entry: BareTagEntry):
        return {"entry_id": entry_id, "entry": entry}

    @app.put("/tag-forms/unique/{entry_id}")
    async def replace_unique_tags(entry_id: int, entry: UniqueTagEntry):
        return {"entry_id": entry_id, "entry": entry}

    @app.put("/assets/{asset_id}")
    async def replace_asset(asset_id: int, asset: ReviewAsset):
        return {"asset_id": asset_id, "asset": asset}

    @app.post("/offers/")
    async def create_offer(offer: ReviewOffer):
        return offer

    @app.post("/image-batches/")
    async def create_image_batch(images: list[ReviewImage]):
        return images

    @app.post("/weight-maps/")
    async def create_weight_map(weights: dict[int, float]):
        return weights

    return app
