from enum import Enum

from fastapi import FastAPI


class AtlasGroup(Enum):
    assets = "assets"
    operators = "operators"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial002b_test_get_items/items/",
        tags=[AtlasGroup.assets],
    )
    async def read_assets():
        return ["cedar", "flint"]

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial002b_test_get_items/users/",
        tags=[AtlasGroup.operators],
    )
    async def read_operators():
        return ["mira", "noor"]

    return app
