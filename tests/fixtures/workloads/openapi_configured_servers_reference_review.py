"""Expose caller-owned server configuration after an OpenAPI request stimulus."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    configured_servers = [
        {"url": "https://catalog.example.invalid/v2", "description": "Catalog base"}
    ]
    app = FastAPI(servers=configured_servers)

    @app.get("/configured-servers", include_in_schema=False)
    def inspect_configured_servers() -> list[dict[str, str]]:
        return configured_servers

    return app
