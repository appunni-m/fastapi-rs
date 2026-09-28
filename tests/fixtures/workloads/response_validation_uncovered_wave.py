"""Independent response-validation and recursive-model HTTP workload."""

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class Item(BaseModel):
    name: str
    price: float | None = None
    owner_ids: list[int] | None = None


@dataclass
class DataclassItem:
    name: str
    price: float | None = None
    owner_ids: list[int] | None = None


class RecursiveItem(BaseModel):
    sub_items: list["RecursiveItem"] = []
    name: str


class RecursiveSubitemInSubmodel(BaseModel):
    sub_items2: list["RecursiveItemViaSubmodel"] = []
    name: str


class RecursiveItemViaSubmodel(BaseModel):
    sub_items1: list[RecursiveSubitemInSubmodel] = []
    name: str


RecursiveItem.model_rebuild()
RecursiveSubitemInSubmodel.model_rebuild()
RecursiveItemViaSubmodel.model_rebuild()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/invalid", response_model=Item)
    def get_invalid() -> dict[str, object]:
        return {"name": "invalid", "price": "foo"}

    @app.get("/items/invalid-none", response_model=Item)
    def get_invalid_none() -> None:
        return None

    @app.get("/items/valid-none", response_model=Item | None)
    def get_valid_none(send_none: bool = False) -> dict[str, object] | None:
        if send_none:
            return None
        return {"name": "invalid", "price": 3.2}

    @app.get("/items/inner-invalid", response_model=Item)
    def get_inner_invalid() -> dict[str, object]:
        return {
            "name": "double invalid",
            "price": "foo",
            "owner_ids": ["foo", "bar"],
        }

    @app.get("/items/invalid-list", response_model=list[Item])
    def get_invalid_list() -> list[dict[str, object]]:
        return [
            {"name": "foo"},
            {"name": "bar", "price": "bar"},
            {"name": "baz", "price": "baz"},
        ]

    @app.get("/dataclass/invalid", response_model=DataclassItem)
    def get_dataclass_invalid() -> dict[str, object]:
        return {"name": "invalid", "price": "foo"}

    @app.get("/dataclass/inner-invalid", response_model=DataclassItem)
    def get_dataclass_inner_invalid() -> dict[str, object]:
        return {
            "name": "double invalid",
            "price": "foo",
            "owner_ids": ["foo", "bar"],
        }

    @app.get("/dataclass/invalid-list", response_model=list[DataclassItem])
    def get_dataclass_invalid_list() -> list[dict[str, object]]:
        return [
            {"name": "foo"},
            {"name": "bar", "price": "bar"},
            {"name": "baz", "price": "baz"},
        ]

    @app.get("/items/recursive", response_model=RecursiveItem)
    def get_recursive() -> dict[str, object]:
        return {"name": "item", "sub_items": [{"name": "subitem", "sub_items": []}]}

    @app.get("/items/recursive-submodel", response_model=RecursiveItemViaSubmodel)
    def get_recursive_submodel() -> dict[str, object]:
        return {
            "name": "item",
            "sub_items1": [
                {
                    "name": "subitem",
                    "sub_items2": [
                        {
                            "name": "subsubitem",
                            "sub_items1": [{"name": "subsubsubitem", "sub_items2": []}],
                        }
                    ],
                }
            ],
        }

    return app
