"""Input workload for the standard-dataclass request-body tutorial."""

from dataclasses import dataclass

from fastapi import FastAPI


@dataclass
class Item:
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    async def create_item(item: Item):
        return item

    return app
