"""Independent response serialization and OpenAPI atlas workload."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from fastapi import APIRouter, FastAPI, Response
from pydantic import BaseModel, Field


class PublicProfile(BaseModel):
    handle: str
    group: str


class PrivateProfile(PublicProfile):
    access_token: str


class CatalogItem(BaseModel):
    label: str = Field(alias="displayLabel")
    amount: float | None = None
    shelf_ids: list[int] | None = None


class OtherPayload(BaseModel):
    title: str
    cost: float


@dataclass
class DatedEntry:
    label: str
    day: date
    amount: float | None = None
    shelf_ids: list[int] | None = None


class GeneratedReceipt(BaseModel):
    reference: int = 200
    note: str = Field(default_factory=lambda: "ready for collection")


def create_app() -> FastAPI:
    app = FastAPI()

    warehouse = APIRouter()
    inventory = APIRouter()

    @inventory.get("/")
    def read_inventory() -> dict[str, str]:
        return {"inventory_code": "copper-7"}

    warehouse.include_router(inventory, prefix="/items")
    app.include_router(warehouse, prefix="/warehouse")

    response_specs = APIRouter()

    @response_specs.get("/alpha", responses={503: {"description": "Service paused"}})
    async def alpha() -> str:
        return "alpha"

    @response_specs.get(
        "/beta",
        responses={
            504: {"description": "Gateway timeout"},
            "4XX": {"description": "Client-side range"},
        },
    )
    async def beta() -> str:
        return "beta"

    @response_specs.get(
        "/gamma",
        responses={
            "401": {"description": "Authentication required"},
            "5xx": {"description": "Server-side range"},
            "default": {"description": "Fallback result"},
        },
    )
    async def gamma() -> str:
        return "gamma"

    @response_specs.get(
        "/delta",
        responses={
            "401": {"description": "Authentication required"},
            "5XX": {"model": PublicProfile},
            "default": {"model": PublicProfile},
        },
    )
    async def delta() -> str:
        return "delta"

    app.include_router(response_specs, prefix="/specimens")

    @app.get("/serialization/complete", response_model=CatalogItem)
    def complete_item() -> dict[str, object]:
        return {"displayLabel": "brass", "amount": 4.5}

    @app.get("/serialization/coerced", response_model=CatalogItem)
    def coerced_item() -> dict[str, str]:
        return {"displayLabel": "nickel", "amount": "3.25"}

    @app.get("/serialization/list", response_model=list[CatalogItem])
    def item_list() -> list[dict[str, object]]:
        return [
            {"displayLabel": "tin"},
            {"displayLabel": "zinc", "amount": 6.0},
            {"displayLabel": "cobalt", "amount": 8.5, "shelf_ids": [2, 5]},
        ]

    @app.get("/dataclasses/record", response_model=DatedEntry)
    def dated_record() -> dict[str, object]:
        return {"label": "meeting", "day": "2026-04-12", "amount": 5.0}

    @app.get("/dataclasses/object", response_model=DatedEntry)
    def dated_object() -> DatedEntry:
        return DatedEntry(label="review", day=date(2026, 5, 17), amount=7.0, shelf_ids=[4])

    @app.get("/dataclasses/coerced", response_model=DatedEntry)
    def dated_coerced() -> dict[str, str]:
        return {"label": "shipment", "day": "2026-06-18", "amount": "9.5"}

    @app.get("/dataclasses/list", response_model=list[DatedEntry])
    def dated_list() -> list[dict[str, object]]:
        return [
            {"label": "first", "day": "2026-07-19"},
            {"label": "second", "day": "2026-07-20", "amount": 3.0},
            {"label": "third", "day": "2026-07-21", "amount": 4.0, "shelf_ids": [7]},
        ]

    @app.get("/dataclasses/object-list", response_model=list[DatedEntry])
    def dated_object_list() -> list[DatedEntry]:
        return [
            DatedEntry(label="fourth", day=date(2026, 8, 22)),
            DatedEntry(label="fifth", day=date(2026, 8, 23), amount=10.0),
        ]

    @app.get("/dataclasses/no-model/object")
    def unmodeled_dated_object() -> DatedEntry:
        return DatedEntry(label="sixth", day=date(2026, 9, 24), amount=11.0, shelf_ids=[1, 8])

    @app.get("/dataclasses/no-model/list")
    def unmodeled_dated_list() -> list[DatedEntry]:
        return [
            DatedEntry(label="seventh", day=date(2026, 10, 25)),
            DatedEntry(label="eighth", day=date(2026, 10, 26), amount=12.0),
        ]

    @app.get("/models/alias-dict", response_model=CatalogItem)
    def alias_dict() -> dict[str, object]:
        return {"displayLabel": "silver", "amount": 2.0}

    @app.get("/models/alias-object", response_model=CatalogItem)
    def alias_object() -> CatalogItem:
        return CatalogItem(displayLabel="gold", amount=12.0)

    @app.get("/models/alias-list", response_model=list[CatalogItem])
    def alias_list() -> list[CatalogItem]:
        return [CatalogItem(displayLabel="lead"), CatalogItem(displayLabel="iron", amount=1.5)]

    @app.get("/models/alias-map", response_model=dict[str, CatalogItem])
    def alias_map() -> dict[str, CatalogItem]:
        return {
            "left": CatalogItem(displayLabel="platinum"),
            "right": CatalogItem(displayLabel="palladium", amount=14.0),
        }

    @app.get(
        "/models/unset-object",
        response_model=CatalogItem,
        response_model_exclude_unset=True,
    )
    def unset_object() -> CatalogItem:
        return CatalogItem(displayLabel="lithium", amount=15.0)

    @app.get(
        "/models/unset-coerced",
        response_model=CatalogItem,
        response_model_exclude_unset=True,
    )
    def unset_coerced() -> dict[str, str]:
        return {"displayLabel": "sodium", "amount": "16.5"}

    @app.get(
        "/models/unset-list",
        response_model=list[CatalogItem],
        response_model_exclude_unset=True,
    )
    def unset_list() -> list[CatalogItem]:
        return [
            CatalogItem(displayLabel="magnesium"),
            CatalogItem(displayLabel="calcium", amount=17.0),
            CatalogItem(displayLabel="argon", amount=18.0, shelf_ids=[3]),
        ]

    @app.get(
        "/models/unset-map",
        response_model=dict[str, CatalogItem],
        response_model_exclude_unset=True,
    )
    def unset_map() -> dict[str, CatalogItem]:
        return {
            "upper": CatalogItem(displayLabel="neon"),
            "lower": CatalogItem(displayLabel="krypton", amount=19.5),
        }

    @app.get("/models/generated-dict", response_model=GeneratedReceipt)
    def generated_from_dict() -> dict[str, int]:
        return {"reference": 200}

    @app.get("/models/generated-object", response_model=GeneratedReceipt)
    def generated_from_object() -> GeneratedReceipt:
        return GeneratedReceipt()

    @app.get("/annotations/no-declaration-model")
    def untyped_profile_model():
        return PrivateProfile(handle="moss", group="field", access_token="private")

    @app.get("/annotations/no-declaration-dict")
    def untyped_profile_dict() -> dict[str, str]:
        return {"handle": "reed", "group": "garden"}

    @app.get("/annotations/inferred-model")
    def inferred_profile_model() -> PublicProfile:
        return PrivateProfile(handle="fern", group="greenhouse", access_token="hidden")

    @app.get("/annotations/inferred-dict")
    def inferred_profile_dict() -> PublicProfile:
        return {"handle": "sage", "group": "orchard", "access_token": "hidden"}

    @app.get("/annotations/inferred-invalid")
    def inferred_profile_invalid() -> PublicProfile:
        return {"group": "meadow"}

    @app.get("/annotations/declaration-wins", response_model=PublicProfile)
    def declared_profile_wins() -> OtherPayload:
        return {"handle": "clover", "group": "plot", "access_token": "hidden"}

    @app.get("/annotations/declaration-disabled", response_model=None)
    def declared_profile_disabled() -> PublicProfile:
        return {"handle": "thyme", "group": "kitchen", "access_token": "visible"}

    @app.get("/annotations/inferred-list")
    def inferred_profile_list() -> list[PublicProfile]:
        return [
            PrivateProfile(handle="basil", group="herbs", access_token="hidden"),
            PublicProfile(handle="mint", group="herbs"),
        ]

    @app.get("/annotations/inferred-union")
    def inferred_union() -> PublicProfile | OtherPayload:
        return OtherPayload(title="supply", cost=21.0)

    @app.get("/annotations/explicit-union", response_model=PublicProfile | OtherPayload)
    def explicit_union() -> PublicProfile | OtherPayload:
        return PublicProfile(handle="lavender", group="flowers")

    @app.get("/annotations/inferred-response")
    def inferred_response() -> Response:
        return Response(content="unmodeled body")

    @app.get("/openapi-alias/default", response_model=CatalogItem)
    def alias_openapi_default() -> dict[str, str]:
        return {"displayLabel": "opal"}

    @app.get(
        "/openapi-alias/field-name",
        response_model=CatalogItem,
        response_model_by_alias=False,
    )
    def alias_openapi_field_name() -> dict[str, str]:
        return {"displayLabel": "jasper"}

    return app
