"""Runtime input workload for the separate-schema FastAPI setting."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, computed_field


class SubItem(BaseModel):
    subname: str
    sub_description: str | None = None
    tags: list[str] = []

    model_config = {"json_schema_serialization_defaults_required": True}


class Item(BaseModel):
    name: str
    description: str | None = None
    sub: SubItem | None = None

    model_config = {"json_schema_serialization_defaults_required": True}


class WithComputedField(BaseModel):
    name: str

    @computed_field
    @property
    def computed_field(self) -> str:
        return f"computed {self.name}"


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI(separate_input_output_schemas=factory_input["separate_input_output_schemas"])

    @app.post("/items/", responses={402: {"model": Item}})
    def create_item(item: Item) -> Item:
        return item

    @app.post("/items-list/")
    def create_item_list(item: list[Item]):
        return item

    @app.get("/items/")
    def read_items() -> list[Item]:
        return [
            Item(
                name="Portal Gun",
                description="Device to travel through the multi-rick-verse",
                sub=SubItem(subname="subname"),
            ),
            Item(name="Plumbus"),
        ]

    @app.post("/with-computed-field/")
    def create_with_computed_field(
        with_computed_field: WithComputedField,
    ) -> WithComputedField:
        return with_computed_field

    return app
