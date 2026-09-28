"""Independent ASGI stimuli for the generated Swagger UI redirect endpoint."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(swagger_ui_oauth2_redirect_url="/docs/redirect")

    @app.get("/items/")
    async def read_items():
        return {"id": "foo"}

    return app
