"""Independent route and schema observations for the deprecated OpenAPI prefix."""

from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI(openapi_prefix="/proxy/v2")

    @app.get("/inventory")
    def inventory(request: Request) -> dict[str, str | None]:
        return {
            "state": "available",
            "root_path": request.scope.get("root_path"),
        }

    return app
