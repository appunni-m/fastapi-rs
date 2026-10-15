"""Independent request app for the FastAPI path-parameter documentation mappings."""

from enum import Enum

from fastapi import FastAPI


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_untyped_item(item_id):
        return {"item_id": item_id}

    @app.get("/typed/items/{item_id}")
    async def read_typed_item(item_id: int):
        return {"item_id": item_id}

    @app.get("/typed-values/{enabled}/{ratio}")
    async def read_scalar_values(enabled: bool, ratio: float):
        return {"enabled": enabled, "ratio": ratio}

    @app.get("/users/me")
    async def read_current_user():
        return {"user_id": "the current user"}

    @app.get("/users/{user_id}")
    async def read_user(user_id: str):
        return {"user_id": user_id}

    @app.get("/duplicate-users")
    async def read_users_first():
        return ["Rick", "Morty"]

    @app.get("/duplicate-users")
    async def read_users_second():
        return ["Bean", "Elfo"]

    @app.get("/models/{model_name}")
    async def get_model(model_name: ModelName):
        if model_name is ModelName.alexnet:
            return {"model_name": model_name, "message": "Deep Learning FTW!"}
        if model_name.value == "lenet":
            return {"model_name": model_name, "message": "LeCNN all the images"}
        return {"model_name": model_name, "message": "Have some residuals"}

    @app.get("/files/{file_path:path}")
    async def read_file(file_path: str):
        return {"file_path": file_path}

    return app
