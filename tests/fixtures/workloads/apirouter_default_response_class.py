"""Observe APIRouter response-class fields through public ASGI behavior."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse


class PlaceholderResponse(JSONResponse):
    media_type = "application/x-placeholder-default"


class AssignedResponse(JSONResponse):
    media_type = "application/x-assigned-default"


RESPONSE_CLASSES = {
    "placeholder": PlaceholderResponse,
    "assigned": AssignedResponse,
}


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    del event_trace

    placeholder_class = RESPONSE_CLASSES[factory_input["placeholder_response_class"]]
    assigned_class = RESPONSE_CLASSES[factory_input["assigned_response_class"]]

    placeholder_router = APIRouter()
    placeholder = placeholder_router.default_response_class
    initial_value = placeholder.value
    placeholder.value = placeholder_class
    placeholder_observation = "|".join(
        (
            str(placeholder_router.default_response_class is placeholder),
            str(placeholder_router.default_response_class.value is placeholder_class),
            placeholder_router.default_response_class.value.__name__,
            initial_value.__name__,
        )
    )

    @placeholder_router.get("/placeholder")
    def placeholder_state() -> str:
        return placeholder_observation

    assigned_router = APIRouter()
    assigned_router.default_response_class = assigned_class
    assigned_observation = "|".join(
        (
            str(assigned_router.default_response_class is assigned_class),
            assigned_router.default_response_class.__name__,
        )
    )

    @assigned_router.get("/assigned")
    def assigned_state() -> str:
        return assigned_observation

    app = FastAPI()
    app.include_router(placeholder_router)
    app.include_router(assigned_router)
    return app
