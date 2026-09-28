"""Independent input workloads for strict OAuth2 password-form behavior."""

from fastapi import Depends, FastAPI, Security
from fastapi.security import OAuth2, OAuth2PasswordRequestFormStrict
from pydantic import BaseModel


class User(BaseModel):
    username: str


def _oauth2(*, auto_error: bool, description: str | None = None) -> OAuth2:
    options = {
        "flows": {
            "password": {
                "tokenUrl": "token",
                "scopes": {
                    "read:users": "Read the users",
                    "write:users": "Create users",
                },
            }
        },
        "auto_error": auto_error,
    }
    if description is not None:
        options["description"] = description
    return OAuth2(**options)


def create_required_app() -> FastAPI:
    app = FastAPI()
    oauth2 = _oauth2(auto_error=True)

    def get_current_user(oauth_header: "str" = Security(oauth2)) -> User:  # noqa: B008
        return User(username=oauth_header)

    @app.post("/login")
    def login(form_data: "OAuth2PasswordRequestFormStrict" = Depends()):  # noqa: B008
        return form_data

    @app.get("/users/me")
    def read_current_user(
        current_user: "User" = Depends(get_current_user),  # noqa: B008
    ) -> User:
        return current_user

    return app


def create_optional_app() -> FastAPI:
    app = FastAPI()
    oauth2 = _oauth2(auto_error=False)

    def get_current_user(oauth_header: str | None = Security(oauth2)) -> User | None:
        if oauth_header is None:
            return None
        return User(username=oauth_header)

    @app.post("/login")
    def login(form_data: OAuth2PasswordRequestFormStrict = Depends()):  # noqa: B008
        return form_data

    @app.get("/users/me")
    def read_users_me(
        current_user: User | None = Depends(get_current_user),  # noqa: B008
    ):
        if current_user is None:
            return {"msg": "Create an account first"}
        return current_user

    return app


def create_optional_described_app() -> FastAPI:
    app = FastAPI()
    oauth2 = _oauth2(auto_error=False, description="OAuth2 security scheme")

    def get_current_user(oauth_header: str | None = Security(oauth2)) -> User | None:  # noqa: B008
        if oauth_header is None:
            return None
        return User(username=oauth_header)

    @app.post("/login")
    def login(form_data: OAuth2PasswordRequestFormStrict = Depends()):  # noqa: B008
        return form_data

    @app.get("/users/me")
    def read_users_me(
        current_user: User | None = Depends(get_current_user),  # noqa: B008
    ):
        if current_user is None:
            return {"msg": "Create an account first"}
        return current_user

    return app
