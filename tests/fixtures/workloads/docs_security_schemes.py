from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import APIKeyCookie, APIKeyQuery

query_api_key = APIKeyQuery(name="api_key", scheme_name="QueryApiKey")
cookie_api_key = APIKeyCookie(name="session_key", scheme_name="CookieSession")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-key")
    async def read_query_key(key: Annotated[str, Security(query_api_key)]) -> dict[str, str]:
        return {"key": key}

    @app.get("/cookie-key")
    async def read_cookie_key(key: Annotated[str, Security(cookie_api_key)]) -> dict[str, str]:
        return {"key": key}

    return app
