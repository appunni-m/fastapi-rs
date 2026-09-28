"""Independent OpenAPI inputs for the top-level security review wave."""

from typing import Annotated

from fastapi import Depends, FastAPI, Security
from fastapi.security import (
    APIKeyCookie,
    APIKeyQuery,
    HTTPBasic,
    HTTPBearer,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
)
from fastapi.security.open_id_connect_url import OpenIdConnect


def create_app() -> FastAPI:
    app = FastAPI()

    cookie_key = APIKeyCookie(
        name="session_key",
        description="Independent session-cookie security description",
    )

    @app.get("/atlas/cookie-key")
    async def read_cookie_key(key: Annotated[str, Security(cookie_key)]) -> dict[str, str]:
        return {"session": key}

    query_key = APIKeyQuery(
        name="access_key",
        description="Independent query-key security description",
    )

    @app.get("/atlas/query-key")
    async def read_query_key(key: Annotated[str, Security(query_key)]) -> dict[str, str]:
        return {"query_key": key}

    basic_realm = HTTPBasic(realm="simple")

    @app.get("/atlas/basic-realm")
    async def read_basic_realm(
        credentials: Annotated[object, Security(basic_realm)],
    ) -> dict[str, str]:
        return {"authenticated": "yes"}

    bearer_description = HTTPBearer(
        description="Independent HTTP Bearer security description",
    )

    @app.get("/atlas/bearer-description")
    async def read_bearer(
        credentials: Annotated[object, Security(bearer_description)],
    ) -> dict[str, str]:
        return {"authenticated": "yes"}

    password_bearer = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)

    @app.get("/atlas/password-token")
    async def read_password_token(
        token: Annotated[str | None, Security(password_bearer)],
    ) -> dict[str, str | None]:
        return {"token": token}

    authorization_code = OAuth2AuthorizationCodeBearer(
        authorizationUrl="/atlas/authorize",
        tokenUrl="/atlas/token",
        description="Independent authorization-code security description",
    )

    @app.get("/atlas/code-token")
    async def read_code_token(
        token: Annotated[str, Security(authorization_code)],
    ) -> dict[str, str]:
        return {"token": token}

    openid_description = OpenIdConnect(
        openIdConnectUrl="/atlas/openid",
        description="Independent OpenID Connect security description",
    )

    @app.get("/atlas/openid-description")
    async def read_openid_description(
        authorization: Annotated[str, Security(openid_description)],
    ) -> dict[str, str]:
        return {"authorization": authorization}

    form_oauth2 = OAuth2(
        flows={
            "password": {
                "tokenUrl": "atlas/token",
                "scopes": {"records:read": "Read records"},
            }
        },
        description="Independent OAuth2 form-flow description",
        auto_error=False,
    )

    @app.post("/atlas/login")
    async def atlas_login(form: Annotated[OAuth2PasswordRequestFormStrict, Depends()]):
        return {"username": form.username}

    @app.get("/atlas/current-user")
    async def atlas_current_user(
        authorization: Annotated[str | None, Security(form_oauth2)],
    ) -> dict[str, str | None]:
        return {"authorization": authorization}

    scopes_oauth2 = OAuth2AuthorizationCodeBearer(
        authorizationUrl="/atlas/authorize-scopes",
        tokenUrl="/atlas/token-scopes",
        scopes={"read": "Read records", "write": "Write records"},
        scheme_name="AtlasScopedOAuth2",
    )

    async def get_scoped_token(
        token: Annotated[str, Depends(scopes_oauth2)],
    ) -> str:
        return token

    @app.get(
        "/atlas/scoped-admin",
        dependencies=[
            Depends(get_scoped_token),
            Security(get_scoped_token, scopes=["read", "write"]),
        ],
    )
    async def read_scoped_admin() -> dict[str, str]:
        return {"access": "granted"}

    return app
