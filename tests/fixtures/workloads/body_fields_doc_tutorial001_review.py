"""Independent embedded-body and field-constraint workload for body-fields tutorial 001."""

from __future__ import annotations

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class SupplyInput(BaseModel):
    title: str
    note: str | None = Field(default=None, max_length=120)
    amount: float = Field(gt=0)
    fee: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/supplies/{supply_id}")
    async def replace_supply(
        supply_id: int,
        supply: SupplyInput = Body(embed=True),  # noqa: B008
    ) -> dict[str, int | SupplyInput]:
        return {"supply_id": supply_id, "supply": supply}

    return app
