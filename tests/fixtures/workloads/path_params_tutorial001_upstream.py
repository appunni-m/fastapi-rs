"""Unannotated path parameter workload from the FastAPI path-parameter guide."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id):
        return {"item_id": item_id}

    return app
