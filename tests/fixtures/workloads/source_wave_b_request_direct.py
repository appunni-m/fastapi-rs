"""Independent route that observes a consumer-provided ASGI client address."""

from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/request/items/{item_id}")
    def read_item(item_id: str, request: Request):
        client_host = request.client.host if request.client is not None else ""
        return {"client_host": client_host, "item_id": item_id}

    return app
