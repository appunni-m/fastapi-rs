"""Independent two-route input for direct FastAPI get_openapi parity."""

from __future__ import annotations

from fastapi import APIRouter


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build distinct-path native routes as inputs; expected output stays in results."""
    router = APIRouter()

    @router.get("/items")
    def items():
        return {"items": []}

    @router.get("/users")
    def users():
        return {"users": []}

    return {
        "two-static-get-routes": {
            "args": [],
            "kwargs": {
                "title": "Two Route OpenAPI Probe",
                "version": "1.0.0",
                "routes": router.routes,
            },
        },
    }
