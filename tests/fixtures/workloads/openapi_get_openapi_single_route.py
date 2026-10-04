"""Independent single-route input for direct FastAPI get_openapi parity."""

from __future__ import annotations

from fastapi import APIRouter


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build one native route as a public argument; expected output stays in results."""
    router = APIRouter()

    @router.get("/items")
    def items():
        return {"items": []}

    return {
        "single-route": {
            "args": [],
            "kwargs": {
                "title": "Single Route OpenAPI Probe",
                "version": "1.0.0",
                "routes": router.routes,
            },
        }
    }
