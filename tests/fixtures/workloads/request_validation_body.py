"""Independently authored request-validation body echo workload."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class PackageInput(BaseModel):
    label: str
    units: int


def create_app() -> FastAPI:
    app = FastAPI(title="Package Intake", version="1.0.0")

    @app.exception_handler(RequestValidationError)
    async def include_invalid_body(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"issues": exc.errors(), "payload": exc.body},
        )

    @app.post("/packages")
    async def create_package(package: PackageInput) -> PackageInput:
        return package

    return app
