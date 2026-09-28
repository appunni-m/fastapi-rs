"""Independent path-validation workload for FastAPI 0.141.1.

The selected route declarations follow ``../fastapi/tests/main.py:40-42``
(``/path/int/{item_id}``), ``:60-62`` (minimum-length path string), and
``:75-77`` (numeric ``Path(gt=3)``). Their corresponding requests/assertions
are ``../fastapi/tests/test_path.py:44-77,80-92``, ``:224-244``, and
``:306-325``. This workload keeps only those source-shaped routes needed by
the independent inputs.
"""

from fastapi import FastAPI, Path


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/path/int/{item_id}")
    def get_int_id(item_id: int):
        return item_id

    @app.get("/path/param-minlength/{item_id}")
    def get_path_param_min_length(item_id: str = Path(min_length=3)):
        return item_id

    @app.get("/path/param-gt/{item_id}")
    def get_path_param_gt(item_id: float = Path(gt=3)):
        return item_id

    return app
