"""Independent ASGI workload for a direct JSONResponse carrying a cookie."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/cookie/")
    def create_cookie() -> JSONResponse:
        response = JSONResponse(content={"message": "Issued a direct response"})
        response.set_cookie(key="wave-session", value="direct-json-cookie")
        return response

    return app
