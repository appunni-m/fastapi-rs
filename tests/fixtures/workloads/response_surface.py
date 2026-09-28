"""Independent response behavior workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Query, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS response workload")

    @app.get("/metadata/")
    async def metadata(response: Response) -> dict[str, str]:
        response.headers["X-Archive"] = "v2"
        response.headers["Content-Language"] = "en-GB"
        return {"message": "Stored"}

    @app.post("/sessions/")
    async def issue_session(response: Response) -> dict[str, str]:
        response.set_cookie("sid", "session-204", httponly=True, samesite="lax", secure=True)
        return {"message": "Session issued"}

    @app.post("/orders/", status_code=201)
    async def create_order(name: Annotated[str, Query(min_length=1)]) -> dict[str, str]:
        return {"name": name}

    @app.get("/items/", status_code=status.HTTP_418_IM_A_TEAPOT)
    async def read_items() -> list[dict[str, str]]:
        return [{"name": "Plumbus"}, {"name": "Portal Gun"}]

    @app.put("/documents/{document_id}", response_class=PlainTextResponse)
    async def update_document(document_id: str) -> PlainTextResponse:
        return PlainTextResponse(f"saved:{document_id}", status_code=202)

    @app.get("/raw-json")
    async def read_raw_json() -> JSONResponse:
        return JSONResponse({"kind": "direct"}, status_code=202, headers={"x-mode": "raw"})

    return app
