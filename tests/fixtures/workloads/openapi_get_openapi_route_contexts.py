"""Independent RouteContext inputs for direct FastAPI get_openapi parity."""

from typing import Annotated

from fastapi import APIRouter, FastAPI, Security
from fastapi.routing import iter_route_contexts
from fastapi.security import HTTPBearer
from pydantic import BaseModel


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build effective route contexts as inputs; expected outputs stay in results."""
    included_router = APIRouter()
    bearer_scheme = HTTPBearer()

    @included_router.get("/public", tags=["public"])
    def read_public(token: Annotated[str, Security(bearer_scheme)]):
        return {"public": True}

    @included_router.get("/private", tags=["private"])
    def read_private():
        return {"private": True}

    included_app = FastAPI()
    included_app.include_router(included_router, prefix="/api")
    public_contexts = [
        context
        for context in iter_route_contexts(included_app.routes)
        if "public" in getattr(context, "tags", [])
    ]

    webhook_app = FastAPI()
    webhook_bearer_scheme = HTTPBearer()

    class Subscription(BaseModel):
        username: str

    @webhook_app.webhooks.post("new-subscription")
    def new_subscription(
        body: Subscription,
        token: Annotated[str, Security(webhook_bearer_scheme)],
    ):
        return None

    webhook_contexts = list(iter_route_contexts(webhook_app.webhooks.routes))

    mutable_methods_app = FastAPI()

    @mutable_methods_app.get("/mutable-methods")
    def mutable_methods():
        return {"ok": True}

    mutable_methods_context = next(
        context
        for context in iter_route_contexts(mutable_methods_app.routes)
        if context.path_format == "/mutable-methods"
    )
    mutable_methods_context.methods.add("POST")

    mutable_responses_app = FastAPI()

    @mutable_responses_app.get("/mutable-responses")
    def mutable_responses():
        return {"ok": True}

    mutable_responses_context = next(
        context
        for context in iter_route_contexts(mutable_responses_app.routes)
        if context.path_format == "/mutable-responses"
    )
    mutable_responses_context.responses[201] = {
        "description": "Created",
        "content": {"application/json": {"example": {"id": 1}}},
    }

    excluded_response_app = FastAPI()
    excluded_response_router = APIRouter()

    @excluded_response_router.get("/hidden")
    def hidden_response():
        return {"hidden": True}

    excluded_response_app.include_router(
        excluded_response_router,
        prefix="/private",
        include_in_schema=False,
    )
    excluded_response_router.routes[0].responses[204] = {"model": str}

    return {
        "filtered-included-route-context": {
            "args": [],
            "kwargs": {
                "title": "Public API",
                "version": "1.0.0",
                "routes": public_contexts,
            },
        },
        "webhook-route-context": {
            "args": [],
            "kwargs": {
                "title": "Webhook API",
                "version": "1.0.0",
                "routes": [],
                "webhooks": webhook_contexts,
            },
        },
        "mutated-route-methods": {
            "args": [],
            "kwargs": {
                "title": "Mutable Methods API",
                "version": "1.0.0",
                "routes": [mutable_methods_context],
            },
        },
        "mutated-route-responses": {
            "args": [],
            "kwargs": {
                "title": "Mutable Responses API",
                "version": "1.0.0",
                "routes": [mutable_responses_context],
            },
        },
        "excluded-included-invalid-response": {
            "args": [],
            "kwargs": {
                "title": "Excluded Included API",
                "version": "1.0.0",
                "routes": excluded_response_app.routes,
            },
        },
    }
