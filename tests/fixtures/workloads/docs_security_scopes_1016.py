"""Independent FastAPI surface for OAuth2 security documentation links."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

_SCOPES = {
    "me": "Read information about the current user.",
    "items": "Read items.",
}


def create_docs_security_scopes_1016_app() -> FastAPI:
    app = FastAPI()
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=_SCOPES)

    async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> dict[str, Any]:
        return {
            "token": token,
            "scopes": security_scopes.scopes,
            "scope_str": security_scopes.scope_str,
        }

    async def get_current_active_user(
        current_user: Annotated[dict[str, Any], Security(get_current_user, scopes=["me"])],
    ) -> dict[str, Any]:
        return current_user

    @app.post("/token")
    async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> dict[str, Any]:
        return {
            "grant_type": form_data.grant_type,
            "username": form_data.username,
            "scopes": form_data.scopes,
            "client_id": form_data.client_id,
        }

    @app.get("/users/me/")
    async def read_users_me(
        current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    ) -> dict[str, Any]:
        return current_user

    @app.get("/users/me/items/")
    async def read_own_items(
        current_user: Annotated[
            dict[str, Any], Security(get_current_active_user, scopes=["items"])
        ],
    ) -> dict[str, Any]:
        return current_user

    @app.get("/status/")
    async def read_system_status(
        current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    ) -> dict[str, Any]:
        return {
            "scopes": current_user["scopes"],
            "scope_str": current_user["scope_str"],
        }

    @app.get("/security-in-dependencies/", dependencies=[Security(get_current_user, scopes=["me"])])
    async def security_in_decorator_dependencies() -> dict[str, bool]:
        return {"ok": True}

    return app
