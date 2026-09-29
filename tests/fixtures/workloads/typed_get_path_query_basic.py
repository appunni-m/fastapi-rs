"""Independent typed GET path/query workload for FastAPI 0.141.1.

The route shape follows ``../fastapi/docs_src/path_params/tutorial002_py310.py:6-8``
and the valid/invalid path inputs in
``../fastapi/tests/test_tutorial/test_path_params/test_tutorial002.py:9-27``.
The optional integer query default follows
``../fastapi/docs_src/query_params/tutorial001_py310.py:8-10`` and its requests
in ``../fastapi/tests/test_tutorial/test_query_params/test_tutorial001.py:21-41``;
invalid integer query validation is exercised at
``../fastapi/tests/test_tutorial/test_query_params/test_tutorial006.py:34-50``.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: int, revision: int = 1) -> dict[str, int]:
        return {"item_id": item_id, "revision": revision}

    return app
