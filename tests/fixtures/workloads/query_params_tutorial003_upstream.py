"""Independent workload for FastAPI 0.141.1 query-parameters tutorial 003."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, q: str | None = None, short: bool = False):
        item = {"item_id": item_id}
        if q:
            item.update({"q": q})
        if not short:
            item.update({"description": "This is an amazing item that has a long description"})
        return item

    return app
