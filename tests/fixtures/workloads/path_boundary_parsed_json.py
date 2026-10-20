"""Small ASGI workload for parsed-JSON path-boundary parity cases.

The routes reproduce the relevant public FastAPI declarations from the pinned
application fixture without importing its tests or storing expected outputs.
"""

from typing import Any

from fastapi import FastAPI, Path


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/path/param-le-ge-int/{item_id}")
    def closed_interval(item_id: int = Path(le=3, ge=1)):
        return item_id

    @app.get("/path/param-maxlength/{item_id}")
    def maximum_length(item_id: str = Path(max_length=3)):
        return item_id

    @app.get("/path/param-min_maxlength/{item_id}")
    def bounded_length(item_id: str = Path(max_length=3, min_length=2)):
        return item_id

    @app.get("/path/param-lt-int/{item_id}")
    def less_than(item_id: int = Path(lt=3)):
        return item_id

    @app.get("/path/param-lt-gt-int/{item_id}")
    def open_interval(item_id: int = Path(lt=3, gt=1)):
        return item_id

    return app
