"""Input workload for combined query, header, and cookie parameter models."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, Header, Query
from pydantic import BaseModel, ConfigDict, Field


class QueryFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shared: int = Field(default=1, ge=1, le=10)
    page: int = Field(default=2, ge=1, le=5)


class ConvertedHeaders(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shared: int = Field(default=20, ge=20, le=30)
    client_build: str = "unreported"
    partner_key: str = Field(default="unassigned", alias="X-Partner-Key")


class LiteralHeaders(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_code: str = "unreported"


class CookiePreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shared: int = Field(default=30, ge=30, le=40)
    theme: str = "light"


def get_request_context(
    search: Annotated[str | None, Query()] = None,
    origin: Annotated[str | None, Header(alias="X-Origin")] = None,
    session_tag: Annotated[str | None, Cookie()] = None,
) -> dict[str, str | None]:
    return {"search": search, "origin": origin, "session_tag": session_tag}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/combined/")
    async def read_combined(
        query: Annotated[QueryFilters, Query()],
        headers: Annotated[ConvertedHeaders, Header()],
        literal_headers: Annotated[LiteralHeaders, Header(convert_underscores=False)],
        cookies: Annotated[CookiePreferences, Cookie()],
        context: Annotated[dict[str, str | None], Depends(get_request_context)],
    ) -> dict[str, object]:
        return {
            "query": query.model_dump(),
            "headers": headers.model_dump(),
            "literal_headers": literal_headers.model_dump(),
            "cookies": cookies.model_dump(),
            "context": context,
        }

    return app
