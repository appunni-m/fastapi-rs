"""Target-only OAuth2 dependency resolution before an injected route failure."""

from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer


def create_app(factory_input: dict[str, Any], workload_trace: list[str]) -> FastAPI:
    del factory_input
    app = FastAPI()
    oauth2_code = OAuth2AuthorizationCodeBearer(
        authorizationUrl="authorize",
        tokenUrl="token",
    )

    async def authorize(token: Annotated[str, Depends(oauth2_code)]) -> str:
        return token

    async def request_resource(
        token: Annotated[str, Depends(authorize)],
    ) -> AsyncIterator[str]:
        del token
        workload_trace.append("dependency-enter")
        try:
            yield "ready"
        finally:
            workload_trace.append("dependency-cleanup")

    @app.get("/protected")
    async def protected(
        resource: Annotated[str, Depends(request_resource)],
    ) -> dict[str, str]:
        return {"resource": resource}

    @app.get("/state")
    async def state() -> dict[str, list[str]]:
        return {"events": list(workload_trace)}

    return app
