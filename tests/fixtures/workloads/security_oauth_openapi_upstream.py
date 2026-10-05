"""Independently authored OAuth2/OpenID Connect security workload."""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Security
from fastapi.security import (
    HTTPBearer,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
)
from fastapi.security.open_id_connect_url import OpenIdConnect


def create_app() -> FastAPI:
    app = FastAPI()

    oauth2_code = OAuth2AuthorizationCodeBearer(
        authorizationUrl="authorize",
        tokenUrl="token",
        scopes={"read": "Read access", "write": "Write access"},
    )

    async def get_code_token(
        token: Annotated[str, Depends(oauth2_code)],
    ) -> str:
        return token

    @app.get("/oauth/code")
    async def read_code_token(
        token: Annotated[str, Security(oauth2_code)],
    ) -> dict[str, str]:
        return {"token": token}

    oauth2_code_described = OAuth2AuthorizationCodeBearer(
        authorizationUrl="authorize",
        tokenUrl="token",
        description="OAuth2 Code Bearer",
        scheme_name="DescribedOAuth2AuthorizationCodeBearer",
    )

    @app.get("/oauth/code-described")
    async def read_described_code_token(
        token: Annotated[str, Security(oauth2_code_described)],
    ) -> dict[str, str]:
        return {"token": token}

    @app.get(
        "/oauth/scopes-via-scheme",
        dependencies=[Security(oauth2_code, scopes=["read", "write"])],
    )
    async def read_with_oauth2_scheme() -> dict[str, str]:
        return {"message": "Scoped access"}

    @app.get(
        "/oauth/scopes-via-helper",
        dependencies=[Security(get_code_token, scopes=["read", "write"])],
    )
    async def read_with_oauth2_helper() -> dict[str, str]:
        return {"message": "Scoped access"}

    router = APIRouter(dependencies=[Security(oauth2_code, scopes=["read"])])

    @router.get("/oauth/items/")
    async def read_items(
        token: Annotated[str, Depends(oauth2_code)],
    ) -> dict[str, str]:
        return {"token": token}

    @router.post("/oauth/items/")
    async def create_item(
        token: Annotated[str, Security(oauth2_code, scopes=["read", "write"])],
    ) -> dict[str, str]:
        return {"token": token}

    app.include_router(router)

    password_bearer_optional = OAuth2PasswordBearer(
        tokenUrl="/token",
        description="OAuth2PasswordBearer security scheme",
        auto_error=False,
    )

    @app.get("/oauth/password-optional/")
    async def read_optional_password_token(
        token: Annotated[str | None, Security(password_bearer_optional)],
    ) -> dict[str, str]:
        if token is None:
            return {"msg": "Create an account first"}
        return {"token": token}

    oauth2_optional = OAuth2(
        flows={
            "password": {
                "tokenUrl": "token",
                "scopes": {"read:users": "Read the users"},
            }
        },
        auto_error=False,
        description="Optional OAuth2 security scheme",
    )

    @app.get("/oauth/generic-optional")
    async def read_optional_oauth2_header(
        authorization: Annotated[str | None, Security(oauth2_optional)],
    ) -> dict[str, str]:
        if authorization is None:
            return {"msg": "Create an account first"}
        return {"username": authorization}

    openid_required = OpenIdConnect(openIdConnectUrl="/openid")

    @app.get("/openid/required")
    async def read_required_openid_header(
        authorization: Annotated[str, Security(openid_required)],
    ) -> dict[str, str]:
        return {"username": authorization}

    openid_described = OpenIdConnect(
        openIdConnectUrl="/openid",
        description="OpenIdConnect security scheme",
        scheme_name="DescribedOpenIdConnect",
    )

    @app.get("/openid/described")
    async def read_described_openid_header(
        authorization: Annotated[str, Security(openid_described)],
    ) -> dict[str, str]:
        return {"username": authorization}

    openid_optional = OpenIdConnect(
        openIdConnectUrl="/openid",
        auto_error=False,
        scheme_name="OptionalOpenIdConnect",
    )

    @app.get("/openid/optional")
    async def read_optional_openid_header(
        authorization: Annotated[str | None, Security(openid_optional)],
    ) -> dict[str, str]:
        if authorization is None:
            return {"msg": "Create an account first"}
        return {"username": authorization}

    root_bearer = HTTPBearer()

    @app.get("/", dependencies=[Depends(root_bearer)])
    async def read_root() -> dict[str, str]:
        return {"message": "Hello, World!"}

    return app
