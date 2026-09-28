"""Independent workload for FastAPI 0.141.1 query-parameters tutorial 005."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_user_item(item_id: str, needy: str):
        return {"item_id": item_id, "needy": needy}

    return app
