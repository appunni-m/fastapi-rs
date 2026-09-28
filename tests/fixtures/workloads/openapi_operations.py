"""Independent route metadata for OpenAPI operation generation inputs."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel, HttpUrl


class MissingRecord(BaseModel):
    code: str
    detail: str


class ConflictRecord(BaseModel):
    reason: str


class CallbackFailure(BaseModel):
    message: str


class FirstVariant(BaseModel):
    first: str


class SecondVariant(BaseModel):
    second: int


class ProductRecord(BaseModel):
    name: str
    cost: float


def _make_invalid_schema_app() -> FastAPI:
    broken = FastAPI()

    @broken.get(
        "/invalid",
        responses={"not-a-status": {"description": "A deliberately malformed status"}},
    )
    async def invalid_status() -> dict[str, str]:
        return {"state": "unused"}

    return broken


def _make_prefixed_app() -> FastAPI:
    prefixed = FastAPI(openapi_prefix="/gateway/v3")

    @prefixed.get("/catalog")
    async def prefixed_catalog() -> dict[str, str]:
        return {"state": "available"}

    return prefixed


def _id(prefix: str) -> Any:
    def generate(route: Any) -> str:
        safe_path = route.path_format.strip("/").replace("/", "_") or "root"
        return f"{prefix}_{route.name}_{safe_path}"

    return generate


def create_app() -> FastAPI:
    app = FastAPI(
        title="Operation Workload",
        version="3.1",
        generate_unique_id_function=_id("app"),
    )

    @app.get(
        "/items/{item_id}",
        responses={
            404: {
                "description": "The requested record is missing",
                "model": MissingRecord,
                "content": {
                    "application/json": {"example": {"code": "missing", "detail": "No record"}}
                },
            },
            409: {"description": "The record is already archived", "model": ConflictRecord},
        },
    )
    async def item_detail(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @app.get(
        "/custom-validation/{item_id}",
        responses={422: {"description": "The identifier is not accepted", "model": MissingRecord}},
    )
    async def custom_validation(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    router = APIRouter(prefix="/router")

    @router.get("/first", responses={501: {"description": "One response from a router"}})
    async def first_router_route() -> dict[str, str]:
        return {"route": "first"}

    @router.get(
        "/second",
        responses={"4XX": {"description": "A ranged response"}},
    )
    async def second_router_route() -> dict[str, str]:
        return {"route": "second"}

    @router.get(
        "/third",
        responses={"default": {"description": "A fallback response"}},
    )
    async def third_router_route() -> dict[str, str]:
        return {"route": "third"}

    @router.get(
        "/fourth",
        responses={"5XX": {"model": ConflictRecord}, "default": {"model": MissingRecord}},
    )
    async def fourth_router_route() -> dict[str, str]:
        return {"route": "fourth"}

    app.include_router(router)

    @app.get(
        "/variants/first",
        responses={
            500: {
                "model": FirstVariant | SecondVariant,
                "content": {"application/json": {"examples": {"first": {"value": {"first": "x"}}}}},
            }
        },
    )
    async def first_variant() -> dict[str, str]:
        return {"first": "x"}

    @app.get(
        "/query-extension",
        openapi_extra={
            "parameters": [
                {
                    "name": "trace_code",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string", "title": "Trace Code"},
                    "x-source": "route-extension",
                }
            ]
        },
    )
    async def query_extension() -> dict[str, str]:
        return {"state": "ready"}

    @app.get(
        "/route-extension",
        openapi_extra={"x-workload-extension": {"revision": 3, "channel": "test"}},
    )
    async def route_extension() -> dict[str, str]:
        return {"state": "ready"}

    @app.get("/hidden/cookie")
    async def hidden_cookie(value: Annotated[str | None, Cookie(include_in_schema=False)] = None):
        return {"value": value or ""}

    @app.get("/hidden/header")
    async def hidden_header(value: Annotated[str | None, Header(include_in_schema=False)] = None):
        return {"value": value or ""}

    @app.get("/hidden/path/{value}")
    async def hidden_path(value: Annotated[str, Path(include_in_schema=False)]):
        return {"value": value}

    @app.get("/hidden/query")
    async def hidden_query(value: Annotated[str | None, Query(include_in_schema=False)] = None):
        return {"value": value or ""}

    @app.post("/products")
    async def create_product(
        product: Annotated[
            ProductRecord,
            Body(media_type="application/vnd.catalog+json", embed=True),
        ],
    ) -> ProductRecord:
        return product

    @app.post("/stores")
    async def create_store(
        product: Annotated[ProductRecord, Body(media_type="application/vnd.catalog+json")],
        featured: Annotated[
            list[ProductRecord] | None,
            Body(media_type="application/vnd.catalog+json"),
        ] = None,
    ) -> dict[str, Any]:
        return {"product": product, "featured": featured or []}

    callback_router = APIRouter()

    @callback_router.get(
        "{$callback_url}/receipt/",
        responses={400: {"description": "A callback-side error", "model": CallbackFailure}},
    )
    async def callback_receipt() -> dict[str, str]:
        return {"state": "received"}

    @app.post("/callback-registration", callbacks=callback_router.routes)
    async def register_callback(callback_url: HttpUrl) -> dict[str, str]:
        return {"state": "registered"}

    @app.post("/ids/top")
    async def top_level_id() -> dict[str, str]:
        return {"scope": "top"}

    router_ids = APIRouter(prefix="/ids", generate_unique_id_function=_id("router"))

    @router_ids.get("/router")
    async def router_id() -> dict[str, str]:
        return {"scope": "router"}

    app.include_router(router_ids)

    included_ids = APIRouter()

    @included_ids.get("/included")
    async def include_override_id() -> dict[str, str]:
        return {"scope": "include"}

    app.include_router(included_ids, prefix="/ids", generate_unique_id_function=_id("include"))

    nested = APIRouter(prefix="/ids/nested")
    nested_leaf = APIRouter(generate_unique_id_function=_id("leaf"))

    @nested_leaf.get("/leaf")
    async def nested_leaf_id() -> dict[str, str]:
        return {"scope": "nested"}

    nested.include_router(nested_leaf)
    app.include_router(nested, generate_unique_id_function=_id("outer"))

    @app.get("/ids/operation-override", generate_unique_id_function=_id("operation"))
    async def operation_override_id() -> dict[str, str]:
        return {"scope": "operation"}

    @app.get("/ids/app-operation-override", generate_unique_id_function=_id("app-operation"))
    async def app_operation_override_id() -> dict[str, str]:
        return {"scope": "app-operation"}

    callback_ids = APIRouter()

    @callback_ids.post("/notify", generate_unique_id_function=_id("callback"))
    async def callback_id() -> dict[str, str]:
        return {"scope": "callback"}

    @app.post("/ids/with-callback", callbacks=callback_ids.routes)
    async def route_with_callback() -> dict[str, str]:
        return {"scope": "callback-owner"}

    @app.get("/openapi-invalid.json", include_in_schema=False)
    async def invalid_openapi() -> dict[str, Any]:
        return _make_invalid_schema_app().openapi()

    prefixed_app = _make_prefixed_app()

    @app.get("/openapi-prefixed.json", include_in_schema=False)
    async def prefixed_openapi() -> dict[str, Any]:
        return prefixed_app.openapi()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"state": "ready"}

    return app
