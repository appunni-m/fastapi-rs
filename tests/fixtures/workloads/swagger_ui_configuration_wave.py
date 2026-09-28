"""Independent FastAPI Swagger UI configuration applications."""

from fastapi import FastAPI


def _make_app(parameters: dict[str, object]) -> FastAPI:
    app = FastAPI(swagger_ui_parameters=parameters)

    @app.get("/users/{username}")
    async def read_user(username: str) -> dict[str, str]:
        return {"message": f"Hello {username}"}

    return app


def create_default_app() -> FastAPI:
    return _make_app({"syntaxHighlight": False})


def create_theme_app() -> FastAPI:
    return _make_app({"syntaxHighlight": {"theme": "obsidian"}})


def create_override_app() -> FastAPI:
    return _make_app({"deepLinking": False})
