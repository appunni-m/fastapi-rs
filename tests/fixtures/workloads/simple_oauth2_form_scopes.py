from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/token")
    async def inspect_form(
        form: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> dict[str, object]:
        return {"scopes": form.scopes, "username": form.username}

    return app
