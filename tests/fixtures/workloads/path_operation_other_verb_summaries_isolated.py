from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/put", summary="Update with PUT")
    async def update_with_put() -> None:
        return None

    @app.patch("/items/patch", summary="Update with PATCH")
    async def update_with_patch() -> None:
        return None

    @app.delete("/items/delete", summary="Delete an item")
    async def delete_item() -> None:
        return None

    @app.options("/items/options", summary="Inspect options")
    async def inspect_options() -> None:
        return None

    @app.head("/items/head", summary="Inspect headers")
    async def inspect_headers() -> None:
        return None

    @app.trace("/items/trace", summary="Trace an item")
    async def trace_item() -> None:
        return None

    return app
