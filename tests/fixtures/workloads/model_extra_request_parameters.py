"""Independent model-extra workload from FastAPI 0.141.1.

Source cases in ``tests/test_query_cookie_header_model_extra_params.py``:
query repeated extras (lines 38-51), repeated header extras (70-84), and
duplicate-cookie last-value behavior (129-140). Route definitions follow the
source's ``Model`` and ``Query``/``Header``/``Cookie`` declarations (8-11,
18-30); this workload is independently authored and contains no assertions.
"""

from __future__ import annotations

from fastapi import Cookie, FastAPI, Header, Query
from pydantic import BaseModel


class ExtraParameters(BaseModel):
    param: str

    model_config = {"extra": "allow"}


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

    return app
