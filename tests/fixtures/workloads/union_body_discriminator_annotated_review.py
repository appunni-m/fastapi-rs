"""Callable Pydantic discriminator through both FastAPI Body declaration forms."""

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Discriminator, Tag


class Cat(BaseModel):
    pet_type: str = "cat"
    meows: int


class Dog(BaseModel):
    pet_type: str = "dog"
    barks: float


def get_pet_type(value):
    assert isinstance(value, dict)
    return value.get("pet_type", "")


Pet = Annotated[
    Annotated[Cat, Tag("cat")] | Annotated[Dog, Tag("dog")],
    Discriminator(get_pet_type),
]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/pet/assignment")
    async def create_pet_assignment(pet: Pet = Body()):  # noqa: B008
        return pet

    @app.post("/pet/annotated")
    async def create_pet_annotated(pet: Annotated[Pet, Body()]):
        return pet

    return app
