"""Independent input workload for the Header conversion documentation section."""

from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel


class HeaderModel(BaseModel):
    request_label: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/default/")
    async def read_default(request_label: Annotated[str | None, Header()] = None):
        return {"request_label": request_label}

    @app.get("/preserved/")
    async def read_preserved(
        request_label: Annotated[str | None, Header(convert_underscores=False)] = None,
    ):
        return {"request_label": request_label}

    @app.get("/model/")
    async def read_model(
        headers: Annotated[HeaderModel, Header(convert_underscores=False)],
    ):
        return {"request_label": headers.request_label}

    return app
