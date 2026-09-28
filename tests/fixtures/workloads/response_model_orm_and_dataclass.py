"""Independent ASGI inputs for attribute-backed and dataclass responses."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict


class ContactInput(BaseModel):
    given_name: str
    family_name: str


class ContactView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    given_name: str
    family_name: str
    label: str


class DirectoryRecord:
    def __init__(self, given_name: str, family_name: str) -> None:
        self.given_name = given_name
        self.family_name = family_name

    @property
    def label(self) -> str:
        return f"{self.family_name}, {self.given_name}"


@dataclass
class CatalogCard:
    card_id: uuid.UUID
    title: str
    amount: float
    keywords: list[str] = field(default_factory=list)
    note: str | None = None
    taxable: bool | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/directory/", response_model=ContactView)
    def add_contact(contact: ContactInput) -> DirectoryRecord:
        return DirectoryRecord(contact.given_name, contact.family_name)

    @app.get("/catalog-card", response_model=CatalogCard)
    def read_catalog_card() -> dict[str, object]:
        return {
            "card_id": uuid.UUID("9a6e7e40-c7f4-4e3a-a774-a83a54a23e91"),
            "title": "Copper kettle",
            "amount": 18.75,
            "keywords": ["kitchen", "pour-over"],
        }

    return app
