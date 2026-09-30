"""Input workload for an authenticated OAuth2 token belonging to an inactive user."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer


def create_app() -> FastAPI:
    app = FastAPI()
    bearer = OAuth2PasswordBearer(tokenUrl="token")

    def get_current_user(
        token: Annotated[str, Depends(bearer)],
    ) -> dict[str, str | bool]:
        users = {
            "active-account": {"username": "active-account", "disabled": False},
            "disabled-account": {"username": "disabled-account", "disabled": True},
        }
        user = users.get(token)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def get_current_active_user(
        current_user: Annotated[dict[str, str | bool], Depends(get_current_user)],
    ) -> dict[str, str | bool]:
        if current_user["disabled"]:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    @app.get("/users/me")
    def read_current_user(
        current_user: Annotated[dict[str, str | bool], Depends(get_current_active_user)],
    ) -> dict[str, str | bool]:
        return current_user

    return app
