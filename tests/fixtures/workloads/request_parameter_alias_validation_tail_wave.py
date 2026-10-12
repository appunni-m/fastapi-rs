"""Independent request-parameter validation-alias workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, Cookie, FastAPI, File, Form, Header


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/wire/body")
    async def body_parameter(
        value: Annotated[
            str,
            Body(
                embed=True,
                alias="published-value",
                validation_alias="wire-value",
            ),
        ],
    ) -> dict[str, str]:
        return {"value": value}

    @app.post("/wire/form")
    async def form_parameter(
        value: Annotated[
            str,
            Form(
                alias="published-value",
                validation_alias="wire-value",
            ),
        ],
    ) -> dict[str, str]:
        return {"value": value}

    @app.post("/wire/file")
    async def file_parameter(
        value: Annotated[
            bytes,
            File(
                alias="published-value",
                validation_alias="wire-value",
            ),
        ],
    ) -> dict[str, int]:
        return {"size": len(value)}

    @app.get("/header-validation-alias")
    async def header_validation_alias(
        value: Annotated[str, Header(validation_alias="wire-header")],
    ) -> dict[str, str]:
        return {"value": value}

    @app.get("/header-alias-validation-alias")
    async def header_alias_validation_alias(
        value: Annotated[
            str,
            Header(alias="public-header", validation_alias="wire-header"),
        ],
    ) -> dict[str, str]:
        return {"value": value}

    @app.get("/cookie-validation-alias")
    async def cookie_validation_alias(
        value: Annotated[str, Cookie(validation_alias="wire-cookie")],
    ) -> dict[str, str]:
        return {"value": value}

    @app.get("/cookie-alias-validation-alias")
    async def cookie_alias_validation_alias(
        value: Annotated[
            str,
            Cookie(alias="public-cookie", validation_alias="wire-cookie"),
        ],
    ) -> dict[str, str]:
        return {"value": value}

    return app
