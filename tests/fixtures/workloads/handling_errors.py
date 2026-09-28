"""Independently authored HTTP error and exception-handler workload."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class CatalogIssue(Exception):
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id


def create_app() -> FastAPI:
    app = FastAPI(title="Catalog Error Contract", version="2.0.0")

    @app.exception_handler(CatalogIssue)
    async def handle_catalog_issue(request: Request, exc: CatalogIssue) -> JSONResponse:
        return JSONResponse(
            status_code=418,
            content={"message": f"Catalog entry {exc.product_id} is unavailable."},
            headers={"X-Catalog-Handler": "domain"},
        )

    @app.get("/products/{product_id}")
    async def read_product(product_id: str) -> dict[str, str]:
        if product_id == "missing":
            raise HTTPException(
                status_code=404,
                detail={"code": "missing", "product_id": product_id},
                headers={"X-Catalog-Error": "not-found"},
            )
        if product_id == "blocked":
            raise HTTPException(status_code=418, detail="This product is unavailable.")
        if product_id == "legacy":
            raise StarletteHTTPException(
                status_code=451,
                detail="This product is restricted.",
                headers={"X-Exception-Origin": "starlette"},
            )
        return {"item": "Copper kettle"}

    @app.get("/creatures/{name}")
    async def read_creature(name: str) -> dict[str, str]:
        if name == "yonder":
            raise CatalogIssue(name)
        return {"creature": name}

    @app.get("/quantities/{quantity}")
    async def read_quantity(quantity: int) -> dict[str, int]:
        return {"quantity": quantity}

    return app
