"""Input workload for callable endpoint parameter binding."""

from functools import partial

from fastapi import FastAPI


def create_app() -> FastAPI:
    def endpoint(prefix: str, q: str | None = None) -> dict[str, str | None]:
        return {"prefix": prefix, "query": q}

    app = FastAPI()
    app.get("/")(partial(endpoint, "catalog"))
    return app
