"""Independent HTML-response routes for Swagger UI escaping observations."""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/ui/init-oauth")
    def oauth_config():
        return get_swagger_ui_html(
            openapi_url="/schema.json",
            title="Source Review UI",
            init_oauth={"appName": "</script><script>"},
        )

    @app.get("/ui/parameters")
    def parameter_config():
        return get_swagger_ui_html(
            openapi_url="/schema.json",
            title="Source Review UI",
            swagger_ui_parameters={"customKey": "<img src=x onerror=alert(1)>"},
        )

    @app.get("/ui/normal")
    def normal_config():
        return get_swagger_ui_html(
            openapi_url="/schema.json",
            title="Source Review UI",
            init_oauth={"clientId": "client-example", "appName": "Regular App"},
        )

    return app
