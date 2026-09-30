"""Independent nested-scope graph for OpenAPI security projection."""

from typing import Annotated

from fastapi import Depends, FastAPI, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes


def create_app() -> FastAPI:
    app = FastAPI()
    bearer = OAuth2PasswordBearer(
        tokenUrl="catalog-token",
        scopes={
            "catalog:admin": "Manage catalog access.",
            "catalog:read": "Read catalog entries.",
            "catalog:write": "Change catalog entries.",
        },
    )

    async def collect_branch_scopes(
        scopes: SecurityScopes,
        token: Annotated[str, Depends(bearer)],
    ) -> list[str]:
        del token
        return scopes.scopes

    async def collect_catalog_access(
        reader: Annotated[list[str], Security(collect_branch_scopes, scopes=["catalog:read"])],
        writer: Annotated[list[str], Security(collect_branch_scopes, scopes=["catalog:write"])],
    ) -> dict[str, list[str]]:
        return {"reader": reader, "writer": writer}

    @app.get("/catalog/items")
    async def list_catalog_items(
        access: Annotated[
            dict[str, list[str]],
            Security(collect_catalog_access, scopes=["catalog:admin"]),
        ],
    ) -> dict[str, list[str]]:
        return access

    return app
