"""Input-only workload for FastAPI's no-media-type OpenAPI behavior."""

from fastapi import FastAPI, Response
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
        response_class=Response,
        responses={500: {"description": "Error", "model": JsonApiError}},
    )
    async def a():
        pass

    @app.get("/b", responses={500: {"description": "Error", "model": Error}})
    async def b():
        pass

    return app
