"""Independent ASGI workload for uncovered top-level FastAPI path inputs.

The route table is authored for this input recipe from the declarations in the
pinned FastAPI ``tests/main.py`` path section (lines 25-142). It contains no
upstream test functions, expected outputs, or oracle imports. Starlette-RS owns
generic route dispatch and response transport; FastAPI-RS owns path parameter
construction, extraction, validation, and error mapping in Rust.
"""

from fastapi import FastAPI, Path


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/text")
    def text_route():
        return "Hello World"

    @app.get("/path/{item_id}")
    def unconstrained_path_route(item_id):
        return item_id

    @app.get("/path/str/{item_id}")
    def string_path_route(item_id: str):
        return item_id

    @app.get("/path/int/{item_id}")
    def integer_path_route(item_id: int):
        return item_id

    @app.get("/path/float/{item_id}")
    def float_path_route(item_id: float):
        return item_id

    @app.get("/path/bool/{item_id}")
    def boolean_path_route(item_id: bool):
        return item_id

    @app.get("/path/param/{item_id}")
    def explicit_path_route(item_id: str | None = Path()):
        return item_id

    @app.get("/path/param-minlength/{item_id}")
    def min_length_path_route(item_id: str = Path(min_length=3)):
        return item_id

    @app.get("/path/param-maxlength/{item_id}")
    def max_length_path_route(item_id: str = Path(max_length=3)):
        return item_id

    @app.get("/path/param-min_maxlength/{item_id}")
    def bounded_length_path_route(item_id: str = Path(min_length=2, max_length=3)):
        return item_id

    @app.get("/path/param-gt/{item_id}")
    def float_greater_than_path_route(item_id: float = Path(gt=3)):
        return item_id

    @app.get("/path/param-gt0/{item_id}")
    def float_positive_path_route(item_id: float = Path(gt=0)):
        return item_id

    @app.get("/path/param-ge/{item_id}")
    def float_greater_or_equal_path_route(item_id: float = Path(ge=3)):
        return item_id

    @app.get("/path/param-lt/{item_id}")
    def float_less_than_path_route(item_id: float = Path(lt=3)):
        return item_id

    @app.get("/path/param-lt0/{item_id}")
    def float_negative_path_route(item_id: float = Path(lt=0)):
        return item_id

    @app.get("/path/param-le/{item_id}")
    def float_less_or_equal_path_route(item_id: float = Path(le=3)):
        return item_id

    @app.get("/path/param-lt-gt/{item_id}")
    def float_open_interval_path_route(item_id: float = Path(gt=1, lt=3)):
        return item_id

    @app.get("/path/param-le-ge/{item_id}")
    def float_closed_interval_path_route(item_id: float = Path(ge=1, le=3)):
        return item_id

    @app.get("/path/param-lt-int/{item_id}")
    def integer_less_than_path_route(item_id: int = Path(lt=3)):
        return item_id

    @app.get("/path/param-gt-int/{item_id}")
    def integer_greater_than_path_route(item_id: int = Path(gt=3)):
        return item_id

    @app.get("/path/param-le-int/{item_id}")
    def integer_less_or_equal_path_route(item_id: int = Path(le=3)):
        return item_id

    @app.get("/path/param-ge-int/{item_id}")
    def integer_greater_or_equal_path_route(item_id: int = Path(ge=3)):
        return item_id

    @app.get("/path/param-lt-gt-int/{item_id}")
    def integer_open_interval_path_route(item_id: int = Path(gt=1, lt=3)):
        return item_id

    @app.get("/path/param-le-ge-int/{item_id}")
    def integer_closed_interval_path_route(item_id: int = Path(ge=1, le=3)):
        return item_id

    return app
