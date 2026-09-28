"""Independent Pydantic response filtering and nested serialization workload."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ValidationInfo, field_validator


class UserCreate(BaseModel):
    email: str
    password: str


class PublicUser(BaseModel):
    email: str


class UserRecord(BaseModel):
    email: str
    password_digest: str


class PetRecord(BaseModel):
    name: str
    owner: UserRecord


class PetView(BaseModel):
    name: str
    owner: PublicUser


class ModelB(BaseModel):
    username: str


class ModelC(ModelB):
    password: str


class ModelA(BaseModel):
    name: str
    description: str | None = None
    foo: ModelB
    tags: dict[str, str] = {}

    @field_validator("name")
    @classmethod
    def require_suffix(cls, value: str, _info: ValidationInfo) -> str:
        if not value.endswith("A"):
            raise ValueError("name must end in A")
        return value


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


_ITEMS = {
    "bar": {
        "name": "Bar",
        "description": "The Bar fighters",
        "price": 62,
        "tax": 20.2,
    }
}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/users/", response_model=PublicUser)
    async def create_user(user: UserCreate) -> UserCreate:
        return user

    @app.get("/pets/{pet_id}", response_model=PetView)
    async def read_pet(pet_id: int) -> PetRecord:
        owner = UserRecord(email="johndoe@example.com", password_digest="private")
        return PetRecord(name=f"Pet {pet_id}", owner=owner)

    @app.get("/pets/", response_model=list[PetView])
    async def read_pets() -> list[PetRecord]:
        owner = UserRecord(email="johndoe@example.com", password_digest="private")
        return [PetRecord(name="Nibbler", owner=owner), PetRecord(name="Zoidberg", owner=owner)]

    @app.get(
        "/items/{item_id}/name", response_model=Item, response_model_include={"name", "description"}
    )
    async def read_item_name(item_id: str) -> dict[str, object]:
        return _ITEMS[item_id]

    @app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
    async def read_item_public(item_id: str) -> dict[str, object]:
        return _ITEMS[item_id]

    @app.get("/model/{name}", response_model=ModelA)
    async def read_model(name: str) -> dict[str, object]:
        nested = ModelC(username="test-user", password="private")
        return {
            "name": name,
            "description": "model-a-desc",
            "foo": nested,
            "tags": {"key1": "value1"},
        }

    return app
