"""Independent single-route input for direct FastAPI get_openapi parity."""

from __future__ import annotations

from fastapi import APIRouter


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build native route inputs as public arguments; expected output stays in results."""
    router = APIRouter()
    tagged_router = APIRouter()

    @router.get("/items")
    def items():
        return {"items": []}

    @tagged_router.get("/catalog", tags=["catalog"])
    def catalog():
        return {"items": []}

    return {
        "single-route": {
            "args": [],
            "kwargs": {
                "title": "Single Route OpenAPI Probe",
                "version": "1.0.0",
                "routes": router.routes,
            },
        },
        "tagged-route": {
            "args": [],
            "kwargs": {
                "title": "Tagged Route OpenAPI Probe",
                "version": "2.0.0",
                "routes": tagged_router.routes,
            },
        },
    }
