"""Nested filtering stimulus from FastAPI 0.141.1's unrelated-model case.

The source route and test are at
``tests/test_response_model_data_filter_no_inheritance.py:37-44, 68-74``.
The endpoint returns a nested model whose classes are unrelated to the
declared response model; this module stores no expected response.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class StoredOwner(BaseModel):
    email: str
    password_hash: str


class PublicOwner(BaseModel):
    email: str


class StoredPet(BaseModel):
    name: str
    owner: StoredOwner


class PublicPet(BaseModel):
    name: str
    owner: PublicOwner


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/pets/{pet_id}", response_model=PublicPet)
    async def read_pet(pet_id: int) -> StoredPet:
        owner = StoredOwner(
            email="johndoe@example.com",
            password_hash="opaque-digest",
        )
        return StoredPet(name="Nibbler", owner=owner)

    return app
