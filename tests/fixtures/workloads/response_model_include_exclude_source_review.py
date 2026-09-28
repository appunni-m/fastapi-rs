"""Independent nested response projection workload for the include/exclude source review."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Detail(BaseModel):
    headline: str
    internal_code: str


class Branch(BaseModel):
    detail: Detail
    status: str


class Envelope(BaseModel):
    title: str
    revision: int
    branch: Branch


def create_app() -> FastAPI:
    app = FastAPI(title="Nested response projections")

    @app.get(
        "/include/model",
        response_model=Branch,
        response_model_include={"status": ..., "detail": {"headline"}},
    )
    def include_model() -> Branch:
        return Branch(
            detail=Detail(headline="dispatch-ready", internal_code="vault-17"),
            status="queued",
        )

    @app.get(
        "/include/dict",
        response_model=Branch,
        response_model_include={"status": ..., "detail": {"headline"}},
    )
    def include_dict() -> dict[str, object]:
        return {
            "detail": {"headline": "replica-ready", "internal_code": "vault-29"},
            "status": "held",
        }

    @app.get(
        "/exclude/model",
        response_model=Branch,
        response_model_exclude={"detail": {"internal_code"}},
    )
    def exclude_model() -> Branch:
        return Branch(
            detail=Detail(headline="catalogued", internal_code="vault-41"),
            status="active",
        )

    @app.get(
        "/exclude/dict",
        response_model=Branch,
        response_model_exclude={"detail": {"internal_code"}},
    )
    def exclude_dict() -> dict[str, object]:
        return {
            "detail": {"headline": "indexed", "internal_code": "vault-53"},
            "status": "paused",
        }

    @app.get(
        "/mixed/model",
        response_model=Envelope,
        response_model_include={"branch", "title"},
        response_model_exclude={"branch": {"status"}},
    )
    def mixed_model() -> Envelope:
        return Envelope(
            title="model record",
            revision=5,
            branch=Branch(
                detail=Detail(headline="model detail", internal_code="vault-67"),
                status="archived",
            ),
        )

    @app.get(
        "/mixed/dict",
        response_model=Envelope,
        response_model_include={"branch", "title"},
        response_model_exclude={"branch": {"status"}},
    )
    def mixed_dict() -> dict[str, object]:
        return {
            "title": "mapping record",
            "revision": 8,
            "branch": {
                "detail": {"headline": "mapping detail", "internal_code": "vault-79"},
                "status": "closed",
            },
        }

    return app
