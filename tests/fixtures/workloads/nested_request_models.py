"""Independent request models for nested bodies and partial record updates."""

from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl


class CatalogImage(BaseModel):
    url: HttpUrl
    caption: str


class CatalogItem(BaseModel):
    title: str
    summary: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = Field(default_factory=set)
    images: list[CatalogImage] | None = None


class PromotionItem(BaseModel):
    title: str
    price: float
    tags: set[str] = Field(default_factory=set)
    images: list[CatalogImage] | None = None


class Promotion(BaseModel):
    title: str
    price: float
    items: list[PromotionItem]


class EditableRecord(BaseModel):
    title: str | None = None
    summary: str | None = None
    price: float | None = None
    surcharge: float = 0.14
    labels: list[str] = Field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI()
    records = {
        "quartz": {
            "title": "Initial notebook",
            "price": 8.25,
            "surcharge": 0.31,
            "labels": ["stationery"],
        }
    }

    @app.put("/catalog/{catalog_id}")
    async def replace_catalog_item(catalog_id: int, item: CatalogItem) -> dict[str, object]:
        return {"catalog_id": catalog_id, "item": item}

    @app.post("/promotions/")
    async def create_promotion(promotion: Promotion) -> Promotion:
        return promotion

    @app.post("/weights/")
    async def create_weights(weights: dict[int, float]) -> dict[int, float]:
        return weights

    @app.get("/records/{record_key}", response_model=EditableRecord)
    async def read_record(record_key: str) -> dict[str, object]:
        return records[record_key]

    @app.put("/records/{record_key}", response_model=EditableRecord)
    async def update_record(record_key: str, patch: EditableRecord) -> dict[str, object]:
        record = records[record_key]
        record.update(patch.model_dump(exclude_unset=True))
        return record

    return app
