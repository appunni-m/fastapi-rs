"""Independent typed request-body workload for body tutorial 001."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class CatalogEntry(BaseModel):
    title: str
    details: str | None = None
    amount: float
    fee: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/catalog/entries")
    async def create_entry(entry: CatalogEntry) -> CatalogEntry:
        return entry

    return app
