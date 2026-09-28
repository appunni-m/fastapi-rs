"""Independent global-header-dependency apps in both tutorial annotation forms."""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


async def verify_token_default(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key_default(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


async def verify_token_annotated(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key_annotated(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


def _build_app(verify_token, verify_key) -> FastAPI:
    app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

    @app.get("/items/")
    async def read_items():
        return [{"item": "Portal Gun"}, {"item": "Plumbus"}]

    @app.get("/users/")
    async def read_users():
        return [{"username": "Rick"}, {"username": "Morty"}]

    return app


def create_app_default() -> FastAPI:
    return _build_app(verify_token_default, verify_key_default)


def create_app_annotated() -> FastAPI:
    return _build_app(verify_token_annotated, verify_key_annotated)
