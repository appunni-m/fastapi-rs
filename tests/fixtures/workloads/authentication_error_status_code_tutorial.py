from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class LegacyForbiddenBearer(HTTPBearer):
    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(status_code=403, detail="A bearer credential is required")


def create_app() -> FastAPI:
    app = FastAPI()
    legacy_bearer = LegacyForbiddenBearer()

    @app.get("/agents/current")
    def read_current_agent(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(legacy_bearer)],
    ) -> dict[str, str]:
        return {"credential": credentials.credentials, "tenant": "north"}

    return app
