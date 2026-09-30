"""Independent probe that distinguishes webhook identifiers from HTTP paths."""

from fastapi import FastAPI
from pydantic import BaseModel


class CatalogEvent(BaseModel):
    snapshot_id: str
    item_count: int


def create_app() -> FastAPI:
    app = FastAPI(title="Catalog Events", version="1.0")

    @app.webhooks.post("catalog-rebuilt")
    def catalog_rebuilt(event: CatalogEvent):
        """Describe the event that a consumer may receive at its registered URL."""

    return app
