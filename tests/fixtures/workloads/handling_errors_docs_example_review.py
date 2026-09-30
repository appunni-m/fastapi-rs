"""Independent HTTP workloads for selected handling-errors documentation examples."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_tutorial001_app() -> FastAPI:
    app = FastAPI()
    entries = {"bluebird": "Bluebird atlas"}

    @app.get("/entries/{entry_key}")
    async def read_entry(entry_key: str) -> dict[str, str]:
        if entry_key not in entries:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"entry": entries[entry_key]}

    return app


def create_tutorial002_app() -> FastAPI:
    app = FastAPI()

    @app.get("/archive/{archive_id}")
    async def read_archive(archive_id: str) -> dict[str, str]:
        if archive_id == "missing":
            raise HTTPException(
                status_code=404,
                detail="Archive unavailable",
                headers={"X-Archive-Problem": "missing"},
            )
        return {"archive": archive_id}

    return app


class SpecimenUnavailable(Exception):
    def __init__(self, specimen_code: str) -> None:
        self.specimen_code = specimen_code


def create_tutorial003_app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(SpecimenUnavailable)
    async def specimen_unavailable_handler(
        request: Request, exc: SpecimenUnavailable
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"message": f"Specimen {exc.specimen_code} is unavailable."},
        )

    @app.get("/specimens/{specimen_code}")
    async def read_specimen(specimen_code: str) -> dict[str, str]:
        if specimen_code == "unknown":
            raise SpecimenUnavailable(specimen_code)
        return {"specimen": specimen_code}

    return app


def create_tutorial006_app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(StarletteHTTPException)
    async def delegated_http_exception_handler(request: Request, exc: Exception):
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def delegated_validation_exception_handler(request: Request, exc: RequestValidationError):
        return await request_validation_exception_handler(request, exc)

    @app.get("/stock/{stock_id}")
    async def read_stock(stock_id: int) -> dict[str, int]:
        if stock_id == 4:
            raise HTTPException(status_code=409, detail="Stock is reserved.")
        return {"stock_id": stock_id}

    return app
