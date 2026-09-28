"""Independent Body/Form/File validation-alias workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI, File, Form


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

    return app
