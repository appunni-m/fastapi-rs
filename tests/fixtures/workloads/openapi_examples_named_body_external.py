"""OpenAPI named Body example using the externalValue form."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel


class CatalogEntry(BaseModel):
    name: str
    price: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/catalog-entry")
    async def update_catalog_entry(
        entry: Annotated[
            CatalogEntry,
            Body(
                openapi_examples={
                    "linked-entry": {
                        "summary": "A catalog entry hosted separately",
                        "externalValue": "https://examples.invalid/catalog-entry.json",
                    }
                }
            ),
        ],
    ) -> CatalogEntry:
        return entry

    return app
