"""Inputs for OAuth2 scopes without the tutorial's JWT/password integrations."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

_USER = {
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "disabled": False,
}


def create_tutorial004_app() -> FastAPI:
    app = FastAPI()
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @app.post("/token")
    async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    ) -> dict[str, str]:
        del form_data
        return {"access_token": "synthetic-user", "token_type": "bearer"}

    async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> dict[str, str | bool]:
        if token != "synthetic-user":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return _USER

    @app.get("/users/me/")
    async def read_users_me(
        current_user: Annotated[dict[str, str | bool], Depends(get_current_user)],
    ) -> dict[str, str | bool]:
        return current_user

    @app.get("/users/me/items/")
    async def read_own_items(
        current_user: Annotated[dict[str, str | bool], Depends(get_current_user)],
    ) -> list[dict[str, str]]:
        return [{"item_id": "Foo", "owner": str(current_user["username"])}]

    return app


def create_tutorial005_app() -> FastAPI:
    app = FastAPI()
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl="token",
        scopes={
            "me": "Read information about the current user.",
            "items": "Read items.",
        },
    )
    token_scopes = {
        "synthetic-me-only": {"me"},
        "synthetic-me-and-items": {"me", "items"},
        "synthetic-no-scopes": set(),
    }

    @app.post("/token")
    async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    ) -> dict[str, str]:
        requested_scopes = set(form_data.scopes)
        if {"me", "items"} <= requested_scopes:
            token = "synthetic-me-and-items"
        elif "me" in requested_scopes:
            token = "synthetic-me-only"
        else:
            token = "synthetic-no-scopes"
        return {"access_token": token, "token_type": "bearer"}

    async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> dict[str, str]:
        required_scopes = security_scopes.scopes
        authenticate_value = (
            f'Bearer scope="{security_scopes.scope_str}"' if required_scopes else "Bearer"
        )
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        available_scopes = token_scopes.get(token)
        if available_scopes is None:
            raise credentials_exception
        for scope in required_scopes:
            if scope not in available_scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return _USER

    async def get_current_active_user(
        current_user: Annotated[dict[str, str], Security(get_current_user, scopes=["me"])],
    ) -> dict[str, str]:
        return current_user

    @app.get("/users/me/")
    async def read_users_me(
        current_user: Annotated[dict[str, str], Depends(get_current_active_user)],
    ) -> dict[str, str]:
        return current_user

    @app.get("/users/me/items/")
    async def read_own_items(
        current_user: Annotated[
            dict[str, str], Security(get_current_active_user, scopes=["items"])
        ],
    ) -> list[dict[str, str]]:
        return [{"item_id": "Foo", "owner": current_user["username"]}]

    @app.get("/status/")
    async def read_system_status(
        current_user: Annotated[dict[str, str], Depends(get_current_user)],
    ) -> dict[str, str]:
        return {"status": "ok"}

    return app
