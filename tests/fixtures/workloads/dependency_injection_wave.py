"""Independent request-scoped dependency injection workload."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.requests import HTTPConnection


class GenericA:
    pass


class GenericB:
    pass


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.marker = 42

    async def paging(q: str | None = None, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return {"q": q, "skip": skip, "limit": limit}

    async def connection_marker(connection: HTTPConnection) -> int:
        return connection.app.state.marker

    async def verified_headers(
        x_token: Annotated[str, Header()], x_key: Annotated[str, Header()]
    ) -> list[dict[str, str]]:
        if x_token != "token-value":
            raise HTTPException(status_code=400, detail="token rejected")
        if x_key != "key-value":
            raise HTTPException(status_code=400, detail="key rejected")
        return [{"label": "north"}, {"label": "south"}]

    async def session() -> Any:
        resource = {"ready": True}
        try:
            yield resource
        finally:
            resource["ready"] = False

    async def lookup_item(item_id: str) -> dict[str, str]:
        items = {
            "portal-gun": {"description": "Portable gateway", "owner": "Morgan"},
            "notebook": {"description": "Field notes", "owner": "Morgan"},
        }
        item = items.get(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return item

    async def current_user() -> str:
        return "Morgan"

    async def active_user(user: Annotated[str, Depends(current_user)]) -> str:
        return user

    def original_params(q: str | None = None, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return {"q": q, "skip": skip, "limit": limit}

    def overridden_params(q: str | None = None) -> dict[str, Any]:
        return {"q": q, "skip": 5, "limit": 10}

    app.dependency_overrides[original_params] = overridden_params

    @app.get("/generic/a")
    async def generic_a(value: Annotated[GenericA, Depends()]) -> dict[str, str]:
        return {"class": type(value).__name__}

    @app.get("/generic/b")
    async def generic_b(value: Annotated[GenericB, Depends()]) -> dict[str, str]:
        return {"class": type(value).__name__}

    @app.get("/connection")
    async def read_connection(marker: Annotated[int, Depends(connection_marker)]) -> int:
        return marker

    @app.get("/items")
    async def read_page(params: Annotated[dict[str, Any], Depends(paging)]) -> dict[str, Any]:
        return params

    @app.get("/catalog")
    async def read_catalog(params: Annotated[dict[str, Any], Depends(paging)]) -> dict[str, Any]:
        return {"filters": params, "labels": ["north", "south", "east"]}

    @app.get("/secured-items")
    async def read_secured_items(
        items: Annotated[list[dict[str, str]], Depends(verified_headers)],
    ) -> list[dict[str, str]]:
        return items

    @app.get("/session")
    async def read_session(resource: Annotated[dict[str, Any], Depends(session)]) -> dict[str, Any]:
        return {"ready": resource["ready"]}

    @app.get("/records/{item_id}")
    async def read_record(item: Annotated[dict[str, str], Depends(lookup_item)]) -> dict[str, str]:
        return item

    @app.get("/users/me")
    async def read_active_user(user: Annotated[str, Depends(active_user)]) -> str:
        return user

    @app.get("/users")
    async def read_users(
        params: Annotated[dict[str, Any], Depends(original_params)],
    ) -> dict[str, Any]:
        return {"message": "User listing", "params": params}

    return app
