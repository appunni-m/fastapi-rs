from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/info")
    async def info():
        return {
            "app_name": "Atlas Static API",
            "admin_email": "input-only@example.invalid",
            "items_per_user": 23,
        }

    return app
