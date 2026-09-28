from datetime import datetime, time, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Body, FastAPI, status
from pydantic import BaseModel, Field


class TimeWindow(BaseModel):
    starts_at: datetime
    duration: timedelta
    local_time: time | None = None


class PersonCreate(BaseModel):
    username: str
    password: str
    display_name: str


class PersonPublic(BaseModel):
    username: str
    display_name: str


class Release(BaseModel):
    name: str
    channel: str


class Offer(BaseModel):
    sku: str = Field(examples=["sku-17"])
    quantity: int = Field(gt=0)


class Diagnostics(BaseModel):
    build: str
    internal_note: str


class StockItem(BaseModel):
    sku: str
    quantity: int


class StockReply(BaseModel):
    item: StockItem
    source: str


def create_app() -> FastAPI:
    app = FastAPI(title="Documentation Schema Workload", version="1.0")

    @app.put("/windows/{window_id}")
    async def set_window(window_id: UUID, window: TimeWindow) -> dict[str, object]:
        return {"window_id": window_id, "window": window}

    @app.post("/people", response_model=PersonPublic, status_code=status.HTTP_201_CREATED)
    async def create_person(person: PersonCreate) -> dict[str, str]:
        return {
            "username": person.username,
            "display_name": person.display_name,
            "password": person.password,
        }

    @app.post(
        "/releases",
        status_code=status.HTTP_201_CREATED,
        tags=["release management"],
        summary="Create a release record",
        response_description="The registered release",
    )
    async def create_release(release: Release) -> Release:
        return release

    @app.post("/offers")
    async def submit_offer(
        offer: Annotated[
            Offer,
            Body(
                openapi_examples={
                    "small-batch": {
                        "summary": "A small offer",
                        "value": {"sku": "sku-17", "quantity": 3},
                    }
                }
            ),
        ],
    ) -> Offer:
        return offer

    @app.get(
        "/diagnostics",
        operation_id="readBuildDiagnostics",
        response_model=Diagnostics,
        response_model_exclude={"internal_note"},
        openapi_extra={"x-owner-team": "platform"},
    )
    async def read_diagnostics() -> Diagnostics:
        return Diagnostics(build="2026.09", internal_note="runner-only detail")

    @app.get("/stock/{sku}", response_model=StockReply, operation_id="readStockItem")
    async def read_stock(sku: str, warehouse: str = "north") -> StockReply:
        return StockReply(
            item=StockItem(sku=sku, quantity=6),
            source=warehouse,
        )

    @app.post("/stock", response_model=StockReply, operation_id="receiveStockItem")
    async def receive_stock(item: StockItem) -> StockReply:
        return StockReply(item=item, source="receiving")

    return app
