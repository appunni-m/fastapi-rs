"""Independent ASGI stimuli for route order after router inclusion."""

from typing import Any

from fastapi import APIRouter, FastAPI, WebSocket
from pydantic import BaseModel
from starlette.responses import PlainTextResponse
from starlette.routing import Route


class ContactCard(BaseModel):
    display_name: str
    region: str


class DirectoryEntry(BaseModel):
    contact: ContactCard
    labels: list[str]


class DirectoryEnvelope(BaseModel):
    entry: DirectoryEntry


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()
    scenario = factory_input["scenario"]

    if scenario == "late-static-before-catch-all":
        catalog = APIRouter()
        app.include_router(catalog, prefix="/catalog")

        @app.get("/catalog/{remaining_path:path}")
        def read_catalog_fallback(remaining_path: str) -> dict[str, str]:
            return {"selected": "app-catch-all", "path": remaining_path}

        @catalog.get("/featured")
        def read_featured_item() -> dict[str, str]:
            return {"selected": "late-static-route", "item": "featured"}

    elif scenario == "later-full-after-partial":
        get_router = APIRouter()
        post_router = APIRouter()

        @get_router.get("/items")
        def read_items() -> dict[str, str]:
            return {"selected": "earlier-get"}

        @post_router.post("/items")
        def create_item() -> dict[str, str]:
            return {"selected": "later-post"}

        app.include_router(get_router, prefix="/api")
        app.include_router(post_router, prefix="/api")

    elif scenario == "partial-only-405":
        router = APIRouter()

        @router.get("/items")
        def read_items() -> list[str]:
            return []

        app.include_router(router, prefix="/api")

    elif scenario == "late-websocket-collision":
        routes = APIRouter()
        app.include_router(routes, prefix="/api")

        @app.websocket("/api/stream")
        async def direct_stream(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("direct")
            await websocket.close()

        @routes.websocket("/stream")
        async def included_stream(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("included")
            await websocket.close()

    elif scenario == "direct-and-late-duplicate":

        @app.get("/registry/record", summary="Direct application registration")
        def read_application_record() -> dict[str, str]:
            return {"selected": "direct-application-route"}

        records = APIRouter()
        app.include_router(records)

        @records.get("/registry/record", summary="Late included-router registration")
        def read_included_record() -> dict[str, str]:
            return {"selected": "late-included-route"}

    elif scenario == "nested-late-response-model":
        application_router = APIRouter()
        app.include_router(application_router, prefix="/workspace")

        member_router = APIRouter()
        application_router.include_router(member_router, prefix="/members")

        detail_router = APIRouter()
        member_router.include_router(detail_router, prefix="/directory")

        @detail_router.get("/{member_id}", response_model=DirectoryEnvelope)
        def read_directory_entry(member_id: str) -> dict[str, Any]:
            return {
                "entry": {
                    "contact": {
                        "display_name": f"Member {member_id}",
                        "region": "north",
                        "private_marker": "filtered-contact-field",
                    },
                    "labels": ["active", "directory"],
                    "private_note": "filtered-entry-field",
                },
                "private_envelope_field": "filtered-envelope-field",
            }

    elif scenario == "mixed-add-route-api-order":

        def generic_first(request: Any) -> PlainTextResponse:
            del request
            return PlainTextResponse("generic-first")

        app.add_route("/generic-first", generic_first, methods=["GET"])

        @app.get("/generic-first")
        def api_after_generic() -> dict[str, str]:
            return {"selected": "api-after-generic"}

        @app.get("/api-first")
        def api_first() -> dict[str, str]:
            return {"selected": "api-first"}

        def generic_after(request: Any) -> PlainTextResponse:
            del request
            return PlainTextResponse("generic-after")

        app.add_route("/api-first", generic_after, methods=["GET"])

    elif scenario == "included-constructor-route-slot-order":

        def generic_item(request: Any) -> PlainTextResponse:
            del request
            return PlainTextResponse("included-generic")

        router = APIRouter(routes=[Route("/items", generic_item, methods=["GET"])])
        app.include_router(router, prefix="/generic-first")

        @app.get("/generic-first/items")
        def api_after_include() -> dict[str, str]:
            return {"selected": "api-after-include"}

        @app.get("/api-first/items")
        def api_before_include() -> dict[str, str]:
            return {"selected": "api-before-include"}

        app.include_router(router, prefix="/api-first")

    elif scenario == "nested-constructor-route-prefix":

        def generic_nested_item(request: Any) -> PlainTextResponse:
            del request
            return PlainTextResponse("nested-generic")

        leaf = APIRouter(routes=[Route("/items", generic_nested_item, methods=["GET"])])
        middle = APIRouter()
        middle.include_router(leaf, prefix="/v1")
        app.include_router(middle, prefix="/api")

        @app.get("/api/v1/items")
        def api_after_nested_include() -> dict[str, str]:
            return {"selected": "api-after-nested-include"}

    elif scenario == "included-constructor-partial-fallback":

        def generic_post(request: Any) -> PlainTextResponse:
            del request
            return PlainTextResponse("generic-post")

        router = APIRouter(routes=[Route("/items", generic_post, methods=["POST"])])
        app.include_router(router, prefix="/api")

        @app.get("/api/items")
        def api_get() -> dict[str, str]:
            return {"selected": "api-get"}

    else:
        raise ValueError(f"unsupported route-order scenario: {scenario}")

    return app
