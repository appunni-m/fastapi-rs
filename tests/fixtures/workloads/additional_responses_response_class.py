"""Independent app for paired response-class additional-response schemas."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class JsonApiResponse(JSONResponse):
    media_type = "application/vnd.api+json"


class Error(BaseModel):
    status: str
    title: str


class JsonApiError(BaseModel):
    errors: list[Error]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/a",
        response_class=JsonApiResponse,
        responses={500: {"description": "Error", "model": JsonApiError}},
    )
    async def a():
        return None

    @app.get("/b", responses={500: {"description": "Error", "model": Error}})
    async def b():
        return None

    return app
