"""Input-only HTTP credential branches from the qftq security audit."""

from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPDigest


def create_app() -> FastAPI:
    app = FastAPI()
    bearer = HTTPBearer()
    optional_digest = HTTPDigest(auto_error=False)
    digest = HTTPDigest()

    @app.get("/bearer/mixed-case")
    def read_mixed_case_bearer(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/digest/optional")
    def read_optional_digest(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(optional_digest)],
    ) -> dict[str, str | None]:
        return {
            "scheme": None if credentials is None else credentials.scheme,
            "credentials": None if credentials is None else credentials.credentials,
        }

    @app.get("/digest/multi")
    def read_multi_directive_digest(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(digest)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    return app
