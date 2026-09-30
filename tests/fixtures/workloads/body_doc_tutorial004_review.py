"""Independent path, query, and typed-body workload for body tutorial 004."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class RevisionInput(BaseModel):
    title: str
    note: str | None = None
    score: float
    penalty: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/revisions/{revision_id}")
    async def replace_revision(
        revision_id: int, revision: RevisionInput, comment: str | None = None
    ) -> dict[str, str | float | int | None]:
        result = {"revision_id": revision_id, **revision.model_dump()}
        if comment:
            result["comment"] = comment
        return result

    return app
