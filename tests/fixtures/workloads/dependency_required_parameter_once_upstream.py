"""Independent required-parameter deduplication app from a FastAPI test module."""

from fastapi import Depends, FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    def get_client_key(client_id: str = Query(...)) -> str:
        return f"{client_id}_key"

    def get_client_tag(client_id: str | None = Query(None)) -> str | None:
        if client_id is None:
            return None
        return f"{client_id}_tag"

    @app.get("/foo")
    def foo_handler(
        client_key: str = Depends(get_client_key),
        client_tag: str | None = Depends(get_client_tag),
    ) -> dict[str, str | None]:
        return {"client_id": client_key, "client_tag": client_tag}

    return app
