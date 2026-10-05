"""Independently authored large response-model workload."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class LargeResponse(BaseModel):
    items: list[dict[str, Any]]
    metadata: dict[str, Any]


def _make_payload() -> dict[str, Any]:
    items = [
        {
            "id": index,
            "name": f"catalog-{index}",
            "values": list(range(25)),
            "meta": {
                "active": True,
                "group": index % 10,
                "tag": f"group-{index % 5}",
            },
        }
        for index in range(300)
    ]
    metadata = {
        "source": "benchmark",
        "version": 1,
        "flags": {"a": True, "b": False, "c": True},
        "notes": ["alpha" * 10, "bravo" * 10, "charlie" * 8],
    }
    return {"items": items, "metadata": metadata}


def create_app() -> FastAPI:
    payload = _make_payload()
    app = FastAPI()

    @app.get("/catalog/large", response_model=LargeResponse)
    def get_large_catalog() -> dict[str, Any]:
        return payload

    return app
