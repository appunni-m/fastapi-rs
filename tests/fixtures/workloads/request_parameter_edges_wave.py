"""Independent query, header, and enum path-parameter workload."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Header, Query

_DEFAULT_QUERY_VALUES = ["amber", "indigo"]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/multi-query/")
    async def multi_query(q: Annotated[list[str] | None, Query()] = None):
        return {"q": q}

    @app.get("/default-query/")
    async def default_query(q: Annotated[list[str], Query()] = _DEFAULT_QUERY_VALUES):
        return {"q": q}

    @app.get("/items/")
    async def hidden_query(
        hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
    ):
        return {"hidden_query": hidden_query or "Not found"}

    @app.get("/header-items/")
    async def read_header(
        strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
    ):
        return {"strange_header": strange_header}

    @app.get("/models/{model_name}")
    async def read_model(model_name: ModelName):
        details = {
            ModelName.alexnet: "Layered vision model",
            ModelName.lenet: "Compact convolution model",
            ModelName.resnet: "Residual network",
        }
        return {"model_name": model_name, "message": details[model_name]}

    return app
