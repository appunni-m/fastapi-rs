"""Input workload reading the ASGI client host through Request."""

from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, request: Request) -> dict[str, str]:
        client_host = request.client.host if request.client is not None else ""
        return {"client_host": client_host, "item_id": item_id}

    return app
