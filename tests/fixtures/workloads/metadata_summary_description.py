"""Minimal app workload for application-level OpenAPI metadata."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(
        title="Metadata API",
        summary="A concise API summary.",
        description="Markdown **description** for the API.",
    )
