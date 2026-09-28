"""Independent ASGI stimuli for FastAPI's Starlette route converters."""

from typing import Annotated

from fastapi import FastAPI, Path, Query
from fastapi.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/int/{param:int}")
    def int_convertor(param: Annotated[int, Path()]):
        return {"int": param}

    @app.get("/float/{param:float}")
    def float_convertor(param: Annotated[float, Path()]):
        return {"float": param}

    @app.get("/path/{param:path}")
    def path_convertor(param: Annotated[str, Path()]):
        return {"path": param}

    @app.get("/query/")
    def query_convertor(param: Annotated[str, Query()]):
        return {"query": param}

    @app.get("/generated-path")
    def generated_path():
        return PlainTextResponse(str(app.url_path_for("path_convertor", param="some/example")))

    return app
