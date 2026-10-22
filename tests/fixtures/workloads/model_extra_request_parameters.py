"""Independent model-extra workload for FastAPI 0.157.0 parity.

Source cases in ``tests/test_query_cookie_header_model_extra_params.py``:
query repeated extras (lines 38-51), repeated header extras (70-84),
duplicate-cookie last-value behavior (129-140), and hyphenated header alias
validation (118-126). Route declarations are independently authored to select
those inputs and contain no assertions.
"""

from __future__ import annotations

from fastapi import Cookie, FastAPI, Header, Query
from pydantic import BaseModel


class ExtraParameters(BaseModel):
    param: str

    model_config = {"extra": "allow"}


class RequiredHyphenHeader(BaseModel):
    x_user_id: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    async def query_model_with_extra(
        data: ExtraParameters = Query(),  # noqa: B008
    ) -> ExtraParameters:
        return data

    @app.get("/header")
    async def header_model_with_extra(
        data: ExtraParameters = Header(),  # noqa: B008
    ) -> ExtraParameters:
        return data

    @app.get("/cookie")
    async def cookie_model_with_extra(
        data: ExtraParameters = Cookie(),  # noqa: B008
    ) -> ExtraParameters:
        return data

    @app.get("/header-requires-hyphen")
    async def header_model_requires_hyphen(
        data: RequiredHyphenHeader = Header(),  # noqa: B008
    ) -> RequiredHyphenHeader:
        return data

    return app
