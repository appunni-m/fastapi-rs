"""Independent paths and router-inclusion workload."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request

router = APIRouter(prefix="/records", tags=["records"])


@router.get("/files/{file_path:path}", name="read_file")
async def read_file(file_path: str, request: Request) -> dict[str, str]:
    route = request.scope["route"]
    return {
        "file_path": file_path,
        "route_name": route.name,
        "route_path": route.path,
    }


@router.get("/{record_id}", name="read_record")
async def read_record(record_id: int, request: Request) -> dict[str, int | str]:
    route = request.scope["route"]
    return {
        "record_id": record_id,
        "route_name": route.name,
        "route_path": route.path,
    }


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS independent routing workload")
    app.include_router(router, prefix="/v1")
    return app
