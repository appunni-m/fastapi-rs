"""Independent workload for FastAPI 0.141.1 query-parameters tutorial 001."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    fake_items_db = [
        {"item_name": "Foo"},
        {"item_name": "Bar"},
        {"item_name": "Baz"},
    ]

    @app.get("/items/")
    async def read_item(skip: int = 0, limit: int = 10):
        return fake_items_db[skip : skip + limit]

    return app
