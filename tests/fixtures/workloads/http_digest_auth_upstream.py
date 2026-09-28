"""Input workload for HTTP Digest credential parsing and challenges."""

from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPDigest


def create_app() -> FastAPI:
    app = FastAPI()
    digest = HTTPDigest(description="Digest access")

    @app.get("/profile")
    def read_profile(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(digest)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    return app
