"""Independent workload for the pinned FastAPI response-headers example."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/headers/")
    async def get_headers() -> JSONResponse:
        return JSONResponse(
            content={"message": "Hello World"},
            headers={"X-Cat-Dog": "alone in the world", "Content-Language": "en-US"},
        )

    return app
