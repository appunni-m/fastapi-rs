"""Focused path-only DELETE workload adapted from FastAPI 0.141.1."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.delete("/items/{item_id}")
    def delete_item(item_id: str):
        return {"item_id": item_id}

    return app
