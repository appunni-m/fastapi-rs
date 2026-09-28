"""Input workload for nested Pydantic dataclasses in request and response models."""

from dataclasses import field

from fastapi import FastAPI
from pydantic.dataclasses import dataclass


@dataclass
class Item:
    name: str
    description: str | None = None


@dataclass
class Author:
    name: str
    items: list[Item] = field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/authors/{author_id}/items/", response_model=Author)
    async def create_author_items(author_id: str, items: list[Item]):
        return {"name": author_id, "items": items}

    @app.get("/authors/", response_model=list[Author])
    def get_authors():
        return [
            {"name": "North Echo"},
            {
                "name": "Violet Frame",
                "items": [
                    {"name": "Travel Light"},
                    {
                        "name": "Glass Signal",
                        "description": "A field guide for long nights",
                    },
                ],
            },
        ]

    return app
