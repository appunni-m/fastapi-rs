"""Input workload for the described HTTP Digest OpenAPI scheme."""

from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import HTTPDigest
from fastapi.security.http import HTTPAuthorizationCredentials


def create_app() -> FastAPI:
    app = FastAPI()
    digest = HTTPDigest(description="HTTPDigest scheme")

    @app.get("/users/me")
    def read_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(digest)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    return app
