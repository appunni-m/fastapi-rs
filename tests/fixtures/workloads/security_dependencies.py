"""Independently authored API-key and OAuth2 dependency workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

archive_key = APIKeyHeader(name="X-Archive-Key", scheme_name="ArchiveKey")
context_key = APIKeyHeader(
    name="X-Context-Key",
    scheme_name="ContextKey",
    auto_error=False,
)
record_bearer = OAuth2PasswordBearer(
    tokenUrl="session/token",
    scheme_name="RecordOAuth2",
    scopes={"records:read": "Read archive records"},
)
optional_bearer = OAuth2PasswordBearer(
    tokenUrl="session/token",
    scheme_name="OptionalRecordOAuth2",
    auto_error=False,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Archive Access API", version="1.0.0")

    @app.get("/archive/private")
    async def read_private_archive(
        key: Annotated[str, Security(archive_key)],
    ) -> dict[str, str]:
        return {"archive_key": key}

    @app.get("/archive/context")
    async def read_archive_context(
        key: Annotated[str | None, Security(context_key)],
    ) -> dict[str, str | None]:
        return {"context_key": key}

    @app.get("/records/{record_id}")
    async def read_record(
        record_id: str,
        token: Annotated[str, Security(record_bearer, scopes=["records:read"])],
    ) -> dict[str, str]:
        return {"record_id": record_id, "token": token}

    @app.get("/preview")
    async def preview_records(
        token: Annotated[str | None, Security(optional_bearer)],
    ) -> dict[str, str | None]:
        return {"token": token}

    return app
