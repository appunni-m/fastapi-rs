"""Independent ASGI input for a quoted None return annotation."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/empty-result", status_code=204)
    def read_empty_result() -> "None":  # noqa: UP037 - the quoted annotation is under test.
        return None

    return app
