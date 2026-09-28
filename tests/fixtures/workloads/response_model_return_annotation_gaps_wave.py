"""Independent inputs for response-model return-annotation gap coverage."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class User(BaseModel):
    name: str
    surname: str


class DatabaseUser(User):
    credential_digest: str


class Item(BaseModel):
    name: str
    price: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/forward-reference-list")
    def forward_reference_list() -> "list[User]":
        return [
            DatabaseUser(name="Ari", surname="North", credential_digest="digest-a"),
            DatabaseUser(name="Bea", surname="West", credential_digest="digest-b"),
        ]

    @app.get("/explicit-dict-extra", response_model=User)
    def explicit_dict_extra():
        return {
            "name": "Caro",
            "surname": "Vale",
            "credential_digest": "private-dict-value",
        }

    @app.get("/explicit-submodel-extra", response_model=User)
    def explicit_submodel_extra():
        return DatabaseUser(name="Drew", surname="Lane", credential_digest="private-model-value")

    @app.get("/inferred-submodel-extra")
    def inferred_submodel_extra() -> User:
        return DatabaseUser(name="Eli", surname="Stone", credential_digest="inferred-private-value")

    @app.get("/explicit-model-over-annotation", response_model=User)
    def explicit_model_over_annotation() -> Item:
        return DatabaseUser(
            name="Faye", surname="Reed", credential_digest="precedence-private-value"
        )

    @app.get("/jsonresponse-annotation")
    def jsonresponse_annotation() -> JSONResponse:
        return JSONResponse(content={"kind": "direct", "sequence": 17})

    @app.get("/invalid-inferred-submodel")
    def invalid_inferred_submodel() -> User:
        return Item(name="wrong-shape", price=8.5)

    return app
