"""Independent HTTP authentication and security dependency workload."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    HTTPDigest,
    OAuth2,
    OAuth2PasswordBearer,
)
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase


def create_app() -> FastAPI:
    app = FastAPI()
    other_scheme = HTTPBase(scheme="Other")
    digest_scheme = HTTPDigest()
    optional_digest = HTTPDigest(auto_error=False)
    raw_oauth = OAuth2(flows={"password": {"tokenUrl": "/token", "scopes": {}}})
    optional_oauth = OAuth2(
        flows={"password": {"tokenUrl": "/token", "scopes": {}}},
        auto_error=False,
    )
    bearer = OAuth2PasswordBearer(tokenUrl="/token")
    basic = HTTPBasic()
    strict_bearer = HTTPBearer()

    @app.get("/security/base")
    async def read_base(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(other_scheme)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/security/digest")
    async def read_digest(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(digest_scheme)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/security/digest-optional")
    async def read_optional_digest(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(optional_digest)],
    ) -> dict[str, str | None]:
        if credentials is None:
            return {"scheme": None}
        return {"scheme": credentials.scheme}

    @app.get("/security/oauth-raw")
    async def read_raw_oauth(authorization: Annotated[str, Security(raw_oauth)]) -> str:
        return authorization

    @app.get("/security/oauth-optional")
    async def read_optional_oauth(
        authorization: Annotated[str | None, Security(optional_oauth)],
    ) -> dict[str, str | None]:
        return {"authorization": authorization}

    @app.get("/security/tutorial-token")
    async def read_tutorial_token(token: Annotated[str, Depends(bearer)]) -> dict[str, str]:
        return {"token": token}

    @app.get("/security/tutorial-user")
    async def read_tutorial_user(token: Annotated[str, Depends(bearer)]) -> dict[str, str]:
        if token != "active-token":
            raise HTTPException(status_code=401, detail="Credentials rejected")
        return {"username": "Morgan"}

    @app.get("/security/basic")
    async def read_basic(
        credentials: Annotated[HTTPBasicCredentials, Depends(basic)],
    ) -> dict[str, str]:
        return {"username": credentials.username, "password": credentials.password}

    @app.get("/security/basic-checked")
    async def check_basic(
        credentials: Annotated[HTTPBasicCredentials, Depends(basic)],
    ) -> dict[str, str]:
        if credentials.username != "stanleyjobson" or credentials.password != "swordfish":
            raise HTTPException(
                status_code=401,
                detail="Credentials rejected",
                headers={"WWW-Authenticate": "Basic"},
            )
        return {"username": credentials.username}

    @app.get("/security/bearer")
    async def read_bearer(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(strict_bearer)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    scoped_oauth = OAuth2PasswordBearer(
        tokenUrl="/scope-token",
        scopes={"scope:read": "Read scoped records", "scope:write": "Write scoped records"},
        scheme_name="ScopedOAuth2",
    )

    async def get_scoped_token(token: Annotated[str, Depends(scoped_oauth)]) -> str:
        return token

    @app.get(
        "/security/scoped-admin",
        dependencies=[
            Security(get_scoped_token, scopes=["scope:read"]),
            Security(get_scoped_token, scopes=["scope:write"]),
        ],
    )
    async def read_scoped_admin() -> dict[str, str]:
        return {"access": "granted"}

    return app
