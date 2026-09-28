"""FastAPI HTTP exception integration and route-parameter request inputs."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Path, Query
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    app = FastAPI()
    items = {"chair": "The blue chair"}

    @app.get("/errors/items/{item_id}")
    async def read_item(item_id: str):
        if item_id not in items:
            raise HTTPException(
                status_code=404,
                detail="Missing item",
                headers={"X-Wave-Error": "item-absent"},
            )
        return {"item": items[item_id]}

    @app.get("/errors/no-body")
    async def no_body():
        raise HTTPException(status_code=204)

    @app.get("/errors/no-body-detail")
    async def no_body_with_detail():
        raise HTTPException(status_code=204, detail="Suppressed by status")

    @app.get("/errors/starlette-items/{item_id}")
    async def read_starlette_item(item_id: str):
        if item_id not in items:
            raise StarletteHTTPException(status_code=404, detail="Missing item")
        return {"item": items[item_id]}

    @app.get("/convert/int/{value:int}")
    async def integer_value(value: int = Path()):
        return {"integer": value}

    @app.get("/convert/float/{value:float}")
    async def float_value(value: float = Path()):
        return {"float": value}

    @app.get("/convert/path/{value:path}")
    async def path_value(value: str = Path()):
        return {"path": value}

    @app.get("/convert/query/")
    async def query_value(value: str = Query()):
        return {"query": value}

    return app
