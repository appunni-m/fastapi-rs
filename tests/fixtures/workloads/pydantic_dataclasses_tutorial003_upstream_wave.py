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


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/authors/{author_id}/items/", response_model=Author)
    async def create_author_items(author_id: str, items: list[Item]):
        return {"name": author_id, "items": items}

    @app.get("/authors/", response_model=list[Author])
    def get_authors():
        return [
            {
                "name": "Breaters",
                "items": [
                    {
                        "name": "Island In The Moon",
                        "description": "A place to be playin' and havin' fun",
                    },
                    {"name": "Holy Buddies"},
                ],
            },
            {
                "name": "System of an Up",
                "items": [
                    {
                        "name": "Salt",
                        "description": "The kombucha mushroom people's favorite",
                    },
                    {"name": "Pad Thai"},
                    {
                        "name": "Lonely Night",
                        "description": "The mostests lonliest nightiest of allest",
                    },
                ],
            },
        ]

    return app
