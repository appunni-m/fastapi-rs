"""Input workload for a standard dataclass response model."""

from dataclasses import dataclass, field

from fastapi import FastAPI


@dataclass
class Item:
    label: str
    quantity: int
    notes: list[str] = field(default_factory=list)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/current", response_model=Item)
    async def read_current_item() -> Item:
        return Item(label="notebook", quantity=3, notes=["grid"])

    return app
