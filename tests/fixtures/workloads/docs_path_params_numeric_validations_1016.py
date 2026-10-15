"""Independent request app for the FastAPI numeric path-parameter mappings."""

from typing import Annotated

from fastapi import FastAPI, Path, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/metadata/items/{item_id}")
    async def read_metadata_item(
        item_id: Annotated[int, Path(title="The ID of the item to get")],
    ):
        return {"item_id": item_id}

    @app.get("/ordered-default/items/{item_id}")
    async def read_default_order(q: str, item_id: int = Path(title="The item ID")):
        return {"item_id": item_id, "q": q}

    @app.get("/ordered-annotated/items/{item_id}")
    async def read_annotated_order(q: str, item_id: Annotated[int, Path(title="The item ID")]):
        return {"item_id": item_id, "q": q}

    @app.get("/keyword-only/items/{item_id}")
    async def read_keyword_only_order(*, item_id: int = Path(title="The item ID"), q: str):
        return {"item_id": item_id, "q": q}

    @app.get("/keyword-only-annotated/items/{item_id}")
    async def read_keyword_only_annotated(
        item_id: Annotated[int, Path(title="The item ID")], q: str
    ):
        return {"item_id": item_id, "q": q}

    @app.get("/ge/items/{item_id}")
    async def read_ge_item(item_id: Annotated[int, Path(title="The item ID", ge=1)], q: str):
        return {"item_id": item_id, "q": q}

    @app.get("/range/items/{item_id}")
    async def read_gt_le_item(
        item_id: Annotated[int, Path(title="The item ID", gt=0, le=1000)], q: str
    ):
        return {"item_id": item_id, "q": q}

    @app.get("/float/items/{item_id}")
    async def read_float_item(
        *,
        item_id: Annotated[int, Path(title="The item ID", ge=0, le=1000)],
        q: str,
        size: Annotated[float, Query(gt=0, lt=10.5)],
    ):
        results = {"item_id": item_id}
        if q:
            results["q"] = q
        if size:
            results["size"] = size
        return results

    return app
