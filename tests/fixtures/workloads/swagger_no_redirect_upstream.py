"""Independent ASGI stimuli for disabling Swagger UI OAuth redirect support."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(swagger_ui_oauth2_redirect_url=None)

    @app.get("/items/")
    async def read_items():
        return {"id": "foo"}

    return app
