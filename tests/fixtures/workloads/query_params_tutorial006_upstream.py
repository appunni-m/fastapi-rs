"""Independent workload for FastAPI 0.141.1 query-parameters tutorial 006."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_user_item(item_id: str, needy: str, skip: int = 0, limit: int | None = None):
        return {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}

    return app
