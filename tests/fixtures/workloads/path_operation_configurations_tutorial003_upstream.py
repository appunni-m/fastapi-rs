from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()
    router = APIRouter()

    @app.post(
        "/items/",
        summary="Create an item",
        description=(
            "Create an item with all the information, name, description, price, tax "
            "and a set of unique tags"
        ),
    )
    async def create_item(item: Item) -> Item:
        return item

    @router.get("/items/router", description="Description from an included APIRouter.")
    def read_router_item() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(router)

    @app.get("/items/docstring")
    async def read_item_from_docstring() -> dict[str, bool]:
        """
        Create an item with all the information:

        - **name**: each item must have a name
        - **description**: a long description
        - **price**: required
        - **tax**: if the item doesn't have tax, you can omit this
        - **tags**: a set of unique tag strings for this item
        """
        return {"ok": True}

    @app.get("/items/empty-description", description="")
    async def read_item_with_empty_description() -> dict[str, bool]:
        """
        Create an item with all the information:

        - **name**: each item must have a name
        - **description**: a long description
        - **price**: required
        - **tax**: if the item doesn't have tax, you can omit this
        - **tags**: a set of unique tag strings for this item
        """
        return {"ok": True}

    @app.get("/items/form-feed", description="Before the break.\fAfter the break.")
    async def read_item_with_form_feed_description() -> dict[str, bool]:
        return {"ok": True}

    return app
