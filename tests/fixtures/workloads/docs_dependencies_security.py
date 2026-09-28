from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)


class CatalogueQuery:
    def __init__(self, term: str | None = None, page_size: int = 4) -> None:
        self.term = term
        self.page_size = page_size


async def require_tenant_key(
    x_tenant_key: Annotated[str, Header(alias="X-Tenant-Key")],
) -> None:
    if x_tenant_key != "tenant-key":
        raise HTTPException(status_code=403, detail="Tenant key rejected")


async def require_review(confirmed: Annotated[bool, Query()]) -> None:
    if not confirmed:
        raise HTTPException(status_code=403, detail="Review confirmation required")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def current_reader(token: Annotated[str, Depends(oauth2_scheme)]) -> dict[str, str]:
    if token != "reader-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": "reader", "scope": "catalog:read"}


class Bearer401(HTTPBearer):
    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(
            status_code=401,
            detail="Authentication credentials are missing",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_bearer(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(Bearer401())],
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials are missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def create_app() -> FastAPI:
    app = FastAPI(dependencies=[Depends(require_tenant_key)])

    @app.get("/catalog")
    async def list_catalogue(
        query: Annotated[CatalogueQuery, Depends(CatalogueQuery)],
    ) -> dict[str, object]:
        return {"term": query.term, "page_size": query.page_size}

    @app.get("/archive", dependencies=[Depends(require_review)])
    async def read_archive() -> dict[str, str]:
        return {"archive": "released"}

    @app.get("/reports")
    async def read_reports() -> dict[str, list[str]]:
        return {"reports": ["weekly"]}

    @app.post("/token")
    async def issue_token(
        form: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> dict[str, str]:
        if form.username != "reader" or form.password != "fixture-password":
            raise HTTPException(status_code=400, detail="Credentials rejected")
        return {"access_token": "reader-token", "token_type": "bearer"}

    @app.get("/users/me")
    async def read_current_user(
        user: Annotated[dict[str, str], Depends(current_reader)],
    ) -> dict[str, str]:
        return user

    @app.get("/me")
    async def read_bearer_subject(
        token: Annotated[str, Depends(require_bearer)],
    ) -> dict[str, str]:
        return {"subject": token}

    return app
