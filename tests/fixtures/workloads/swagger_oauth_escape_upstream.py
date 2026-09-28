"""Independent ASGI stimuli for Swagger OAuth configuration and HTML escaping."""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html


def create_app() -> FastAPI:
    app = FastAPI(
        swagger_ui_init_oauth={"clientId": "the-foo-clients", "appName": "The Predendapp"}
    )

    @app.get("/items/")
    async def read_items():
        return {"id": "foo"}

    @app.get("/helper/init-oauth")
    async def init_oauth_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Test",
            init_oauth={"appName": "Evil</script><script>alert(1)</script>"},
        )

    @app.get("/helper/parameters")
    async def parameter_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Test",
            swagger_ui_parameters={"customKey": "<img src=x onerror=alert(1)>"},
        )

    @app.get("/helper/normal-oauth")
    async def normal_oauth_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Test",
            init_oauth={"clientId": "my-client", "appName": "My App"},
        )

    return app
