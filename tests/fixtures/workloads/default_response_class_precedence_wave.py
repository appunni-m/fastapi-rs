"""Independent ASGI workload for application response-class defaults."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse


class TaggedJSONResponse(JSONResponse):
    media_type = "application/vnd.fastapi-rs.wave+json"


def create_app() -> FastAPI:
    app = FastAPI(default_response_class=TaggedJSONResponse)

    @app.get("/")
    def application_default():
        return {"owner": "application"}

    return app
