"""Independently authored HTTP workload for response-model tutorial cases."""

from __future__ import annotations

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel


class Tutorial001Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


class Tutorial002User(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None


class Tutorial003UserInput(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None


class Tutorial003UserOutput(BaseModel):
    username: str
    email: str
    full_name: str | None = None


class Tutorial003BaseUser(BaseModel):
    username: str
    email: str
    full_name: str | None = None


class Tutorial003DerivedUser(Tutorial003BaseUser):
    password: str


class Tutorial004Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


class Tutorial006Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


_TUTORIAL004_ITEMS = {
    "omitted": {"name": "Omitted", "price": 21.5},
    "explicit": {
        "name": "Explicit",
        "description": "present in source data",
        "price": 32,
        "tax": 4.5,
    },
}

_TUTORIAL006_ITEM = {
    "name": "Selected",
    "description": "public details",
    "price": 62,
    "tax": 20.2,
}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/tutorial001/items/", response_model=list[Tutorial001Item])
    async def list_tutorial001_items() -> list[dict[str, object]]:
        return [
            {"name": "Portal Device", "price": 42},
            {"name": "Transit Object", "price": 32},
        ]

    @app.post("/tutorial001/items/", response_model=Tutorial001Item)
    async def create_tutorial001_item(item: Tutorial001Item) -> Tutorial001Item:
        return item

    @app.post("/tutorial002/users/", response_model=Tutorial002User)
    async def create_tutorial002_user(user: Tutorial002User) -> Tutorial002User:
        return user

    @app.post("/tutorial003/users/", response_model=Tutorial003UserOutput)
    async def create_tutorial003_user(user: Tutorial003UserInput) -> Tutorial003UserInput:
        return user

    @app.post("/tutorial003-01/users/")
    async def create_tutorial003_01_user(
        user: Tutorial003DerivedUser,
    ) -> Tutorial003BaseUser:
        return user

    @app.get("/tutorial003-02/portal")
    async def tutorial003_02_portal(teleport: bool = False) -> Response:
        if teleport:
            return RedirectResponse(url="https://example.test/portal-destination")
        return JSONResponse(content={"message": "Portal is ready."})

    @app.get("/tutorial003-03/teleport")
    async def tutorial003_03_teleport() -> RedirectResponse:
        return RedirectResponse(url="https://example.test/teleport-destination")

    @app.get("/tutorial003-05/portal", response_model=None)
    async def tutorial003_05_portal(teleport: bool = False) -> Response | dict[str, str]:
        if teleport:
            return RedirectResponse(url="https://example.test/portal-destination")
        return {"message": "Portal is ready."}

    @app.get(
        "/tutorial004/items/{item_id}",
        response_model=Tutorial004Item,
        response_model_exclude_unset=True,
    )
    async def tutorial004_read_item(item_id: str) -> dict[str, object]:
        return _TUTORIAL004_ITEMS[item_id]

    @app.get(
        "/tutorial006/items/{item_id}/name",
        response_model=Tutorial006Item,
        response_model_include={"name", "description"},
    )
    async def tutorial006_read_name(item_id: str) -> dict[str, object]:
        return _TUTORIAL006_ITEM

    @app.get(
        "/tutorial006/items/{item_id}/public",
        response_model=Tutorial006Item,
        response_model_exclude={"tax"},
    )
    async def tutorial006_read_public(item_id: str) -> dict[str, object]:
        return _TUTORIAL006_ITEM

    return app
