"""Independent workload for FastAPI 0.141.1 query-parameters tutorial 004."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/users/{user_id}/items/{item_id}")
    async def read_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
        item = {"item_id": item_id, "owner_id": user_id}
        if q:
            item.update({"q": q})
        if not short:
            item.update({"description": "This is an amazing item that has a long description"})
        return item

    return app
