"""Independent workloads for yield dependencies that suppress or re-raise errors."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException


class InternalError(Exception):
    pass


class OwnerError(Exception):
    pass


def create_app() -> FastAPI:
    app = FastAPI()
    exception_messages: list[str] = []
    items = {
        "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
        "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
    }

    def get_username_translating():
        try:
            yield "Rick"
        except OwnerError as error:
            raise HTTPException(status_code=400, detail=f"Owner error: {error}") from error

    def find_owned_item(item_id: str, username: str) -> dict[str, str]:
        if item_id not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        item = items[item_id]
        if item["owner"] != username:
            raise OwnerError(username)
        return item

    @app.get("/translate/default/items/{item_id}")
    def translate_default(item_id: str, username: str = Depends(get_username_translating)):
        return find_owned_item(item_id, username)

    @app.get("/translate/annotated/items/{item_id}")
    def translate_annotated(
        item_id: str,
        username: Annotated[str, Depends(get_username_translating)],
    ):
        return find_owned_item(item_id, username)

    def get_username_suppressing():
        try:
            yield "Rick"
        except InternalError as error:
            exception_messages.append(str(error))

    def get_username_reraising():
        try:
            yield "Rick"
        except InternalError as error:
            exception_messages.append(str(error))
            raise

    def resolve_item(item_id: str, username: str) -> str:
        if item_id == "portal-gun":
            raise InternalError(f"The portal gun is too dangerous to be owned by {username}")
        if item_id != "plumbus":
            raise HTTPException(
                status_code=404,
                detail="Item not found, there's only a plumbus here",
            )
        return item_id

    @app.get("/suppress/default/{item_id}")
    def suppress_default(item_id: str, username: str = Depends(get_username_suppressing)):
        return resolve_item(item_id, username)

    @app.get("/suppress/annotated/{item_id}")
    def suppress_annotated(
        item_id: str,
        username: Annotated[str, Depends(get_username_suppressing)],
    ):
        return resolve_item(item_id, username)

    @app.get("/reraise/default/{item_id}")
    def reraise_default(item_id: str, username: str = Depends(get_username_reraising)):
        return resolve_item(item_id, username)

    @app.get("/reraise/annotated/{item_id}")
    def reraise_annotated(
        item_id: str,
        username: Annotated[str, Depends(get_username_reraising)],
    ):
        return resolve_item(item_id, username)

    @app.get("/exception-messages")
    def read_exception_messages():
        return {"messages": list(exception_messages)}

    return app
