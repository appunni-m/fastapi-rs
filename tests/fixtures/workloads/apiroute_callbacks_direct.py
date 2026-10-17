"""Direct APIRoute callback constructor and OpenAPI parity inputs."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.routing import APIRoute
from pydantic import BaseModel


class CallbackEvent(BaseModel):
    event_id: int
    accepted: bool


def receive_event(event: CallbackEvent) -> CallbackEvent:
    return event


def create_notification() -> CallbackEvent:
    return CallbackEvent(event_id=1, accepted=True)


def create_argument_bundles() -> dict[str, dict[str, object]]:
    callback_router = APIRouter()
    callback_router.post(
        "{$callback_url}/events/{$request.body.event_id}",
        response_model=CallbackEvent,
        name="receive_event",
    )(receive_event)
    callback_routes = callback_router.routes
    parent_route = APIRoute(
        "/notifications",
        create_notification,
        methods=["post"],
        response_model=CallbackEvent,
        callbacks=callback_routes,
    )
    return {
        "parent-route": {
            "args": ["/notifications", create_notification],
            "kwargs": {
                "methods": ["post"],
                "response_model": CallbackEvent,
                "callbacks": callback_routes,
            },
        },
        "parent-openapi": {
            "args": [],
            "kwargs": {
                "title": "Direct APIRoute Callback Probe",
                "version": "1.0.0",
                "routes": [parent_route],
            },
        },
    }
