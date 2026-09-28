"""Input workload for an app-level OAuth2 authorization dependency."""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer


def create_app() -> FastAPI:
    oauth2_scheme = OAuth2AuthorizationCodeBearer(
        authorizationUrl="authorize",
        tokenUrl="token",
        auto_error=True,
        scopes={"read": "Read access", "write": "Write access"},
    )

    async def get_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
        return token

    app = FastAPI(dependencies=[Depends(get_token)])

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "Hello World"}

    return app
