"""Independent OpenAPI webhook and ordinary route inputs."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel


class AuditRecord(BaseModel):
    actor: str
    sequence: int
    observed_at: datetime


def create_app() -> FastAPI:
    app = FastAPI(title="Audit Interface Probe", version="3.7")

    @app.webhooks.post("audit-record-added")
    def audit_record_added(record: AuditRecord):
        """Describe the record notification sent to a registered consumer."""

    @app.get("/accounts/")
    def read_accounts():
        return ["Aster", "Nova"]

    return app
