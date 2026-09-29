"""Independent PUT route with no declared request body."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/{item_id}")
    def save_item_no_body(item_id: str):
        return {"item_id": item_id}

    return app
