"""Independent workload for response-model and return-annotation behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from fastapi import FastAPI, Response
from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str


class User(BaseUser):
    surname: str


class DBUser(User):
    password_hash: str


class Item(BaseModel):
    name: str
    price: float


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/decorator-precedence", response_model=User)
    def decorator_precedence() -> Item:
        # The explicit response model takes precedence over the return annotation.
        return cast(
            Item,
            {"name": "John", "surname": "Doe", "password_hash": "secret"},
        )

    @app.get("/annotation-none", response_model=None)
    def annotation_none() -> User:
        return DBUser(name="John", surname="Doe", password_hash="secret")

    @app.get("/passthrough")
    def response_passthrough() -> Response:
        return Response(content="Foo")

    @app.get("/users", response_model=list[User])
    def list_users():
        return [
            DBUser(name="John", surname="Doe", password_hash="secret"),
            DBUser(name="Jane", surname="Does", password_hash="secret2"),
        ]

    @app.get("/union-user", response_model=User | Item)
    def union_user():
        return DBUser(name="John", surname="Doe", password_hash="secret")

    @app.get("/union-item", response_model=User | Item)
    def union_item():
        return Item(name="Foo", price=42.0)

    @app.get("/invalid-output", response_model=User)
    def invalid_output():
        return {"name": "John"}

    return app
