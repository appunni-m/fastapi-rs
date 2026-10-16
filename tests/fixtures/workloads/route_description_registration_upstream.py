"""Independent description inputs for generic FastAPI route registration."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.api_route(
        "/items/{item_id}",
        description="Description from FastAPI.api_route.",
    )
    def read_item(item_id: str) -> dict[str, str]:
        return {"item_id": item_id}

    def read_unannotated_item(item_id: str) -> dict[str, str]:
        return {"item_id": item_id}

    app.add_api_route(
        "/items-unannotated/{item_id}",
        read_unannotated_item,
        methods=["GET"],
        description="Description from FastAPI.add_api_route.",
    )
    return app
