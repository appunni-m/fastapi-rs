"""Input workload for the FastAPI status-module re-export contract."""

from fastapi import FastAPI, status
from starlette import status as starlette_status


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/status")
    def read_status_namespace() -> dict[str, object]:
        return {
            "module_identity_matches": status is starlette_status,
            "public_names": list(status.__all__),
            "exports": {name: getattr(status, name) for name in sorted(status.__all__)},
        }

    return app
