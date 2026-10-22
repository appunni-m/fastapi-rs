"""Exercise OAuth2PasswordBearer raw auto_error values through public routes."""

from typing import Annotated, Any

from fastapi import FastAPI, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordBearer as OAuth2PasswordBearerModule


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    scheme = OAuth2PasswordBearer(
        tokenUrl="/token",
        auto_error=factory_input["auto_error"],
    )
    app = FastAPI()

    def scheme_state() -> dict[str, Any]:
        return {
            "auto_error": scheme.auto_error,
            "auto_error_type": type(scheme.auto_error).__name__,
            "root_module_alias_identity": OAuth2PasswordBearer is OAuth2PasswordBearerModule,
        }

    @app.get("/state")
    async def read_state() -> dict[str, Any]:
        return scheme_state()

    @app.get("/set-auto-error")
    async def set_auto_error() -> dict[str, Any]:
        scheme.auto_error = factory_input["set_auto_error"]
        return scheme_state()

    @app.get("/protected")
    async def protected(
        token: Annotated[str | None, Security(scheme)],
    ) -> dict[str, str | None]:
        return {"token": token}

    return app
