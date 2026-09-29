from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/items/put", operation_id="replaceItemPut")
    async def put_item() -> None:
        return None

    @app.patch("/items/patch", operation_id="updateItemPatch")
    async def patch_item() -> None:
        return None

    @app.delete("/items/delete", operation_id="deleteItem")
    async def delete_item() -> None:
        return None

    @app.options("/items/options", operation_id="inspectOptions")
    async def options_item() -> None:
        return None

    @app.head("/items/head", operation_id="inspectHeaders")
    async def head_item() -> None:
        return None

    @app.trace("/items/trace", operation_id="traceItem")
    async def trace_item() -> None:
        return None

    return app
