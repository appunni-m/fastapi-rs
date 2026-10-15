"""Independent ASGI inputs for Bigger Applications tutorial sections."""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    """Build a compact app for the selected router-composition scenario."""
    del event_trace
    scenario = factory_input.get("scenario", "main")

    if scenario == "repeat":
        shared = APIRouter()

        @shared.get("/records")
        async def read_shared_record():
            return {"kind": "shared-record"}

        app = FastAPI()
        app.include_router(shared, prefix="/api/v1")
        app.include_router(shared, prefix="/api/latest")
        return app

    if scenario == "nested":
        members = APIRouter()

        @members.get("/before")
        async def read_member_before_include():
            return {"kind": "member-before-include"}

        internal = APIRouter()
        internal.include_router(members, prefix="/records")
        app = FastAPI()
        app.include_router(internal, prefix="/internal")

        @members.get("/after")
        async def read_member_after_include():
            return {"kind": "member-after-include"}

        return app

    async def require_query_token(token: str) -> None:
        if token != "permit":
            raise HTTPException(status_code=400, detail="query token rejected")

    async def require_header_token(x_token: str = Header()) -> None:
        if x_token != "allow-router-workload":
            raise HTTPException(status_code=400, detail="router header rejected")

    app = FastAPI(dependencies=[Depends(require_query_token)])

    users = APIRouter()

    @users.get("/users/me", tags=["users"])
    async def read_current_user():
        return {"account": "current-user"}

    app.include_router(users)

    items = APIRouter(
        prefix="/items",
        tags=["items"],
        dependencies=[Depends(require_header_token)],
        responses={404: {"description": "Record is unavailable"}},
    )

    @items.get("/{record_id}")
    async def read_item(record_id: str):
        if record_id != "sample":
            raise HTTPException(status_code=404, detail="record is unavailable")
        return {"record_id": record_id, "kind": "router-item"}

    @items.put(
        "/{record_id}",
        tags=["custom"],
        responses={403: {"description": "Operation forbidden"}},
    )
    async def update_custom_item(record_id: str):
        if record_id != "sample":
            raise HTTPException(status_code=403, detail="custom update rejected")
        return {"record_id": record_id, "kind": "custom-item-update"}

    app.include_router(items)

    admin = APIRouter()

    @admin.post("/")
    async def submit_admin_action():
        return {"kind": "admin-action"}

    app.include_router(
        admin,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(require_header_token)],
        responses={418: {"description": "Administrative route marker"}},
    )

    @app.get("/")
    async def read_root():
        return {"kind": "application-root"}

    return app
