"""Independent workloads for yield dependencies that suppress or re-raise errors."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException


class InternalError(Exception):
    pass


def create_app() -> FastAPI:
    app = FastAPI()
    exception_messages: list[str] = []

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
