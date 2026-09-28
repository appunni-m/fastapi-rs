from enum import Enum

from fastapi import FastAPI


class AtlasHue(str, Enum):
    coral = "coral"
    indigo = "indigo"
    teal = "teal"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/atlas/test_path_params_test_tutorial005_test_get_enums_alexnet/models/{model_name}")
    async def choose_hue(model_name: AtlasHue):
        if model_name is AtlasHue.coral:
            return {"selection": model_name, "label": "warm"}
        if model_name is AtlasHue.indigo:
            return {"selection": model_name, "label": "deep"}
        return {"selection": model_name, "label": "clear"}

    return app
