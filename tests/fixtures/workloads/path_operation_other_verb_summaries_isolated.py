from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/put", summary="Update with PUT", tags=["put-items"])
    async def update_with_put() -> None:
        return None

    @app.patch("/items/patch", summary="Update with PATCH", tags=["patch-items"])
    async def update_with_patch() -> None:
        return None

    @app.delete("/items/delete", summary="Delete an item", tags=["delete-items"])
    async def delete_item() -> None:
        return None

    @app.options("/items/options", summary="Inspect options", tags=["options-items"])
    async def inspect_options() -> None:
        return None

    @app.head("/items/head", summary="Inspect headers", tags=["head-items"])
    async def inspect_headers() -> None:
        return None

    @app.trace("/items/trace", summary="Trace an item", tags=["trace-items"])
    async def trace_item() -> None:
        return None

    return app
