"""Independent applications for Swagger UI configuration inputs."""

from __future__ import annotations

from fastapi import FastAPI


def _configured_app(parameters: dict[str, object]) -> FastAPI:
    app = FastAPI(swagger_ui_parameters=parameters)

    @app.get("/members/{member_name}")
    async def read_member(member_name: str):
        return {"greeting": f"Hello {member_name}"}

    return app


def create_app() -> FastAPI:
    app = FastAPI(openapi_url=None)
    app.mount(
        "/syntax-off",
        _configured_app({"syntaxHighlight": False}),
    )
    app.mount(
        "/theme",
        _configured_app({"syntaxHighlight": {"theme": "oceanic"}}),
    )
    app.mount(
        "/deep-link-off",
        _configured_app({"deepLinking": False}),
    )
    return app
