"""Independent public-class and application-instance observation."""

from __future__ import annotations

import fastapi.applications as fastapi_applications
from fastapi import FastAPI
from starlette.applications import Starlette


def create_app(_factory_input: dict[str, object], _workload_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.get("/class-contract")
    def read_class_contract() -> dict[str, bool]:
        return {
            "root_binding_matches_applications_module": (FastAPI is fastapi_applications.FastAPI),
            "fastapi_binding_is_class": isinstance(FastAPI, type),
            "direct_starlette_base": FastAPI.__bases__ == (Starlette,),
            "instance_has_fastapi_type": type(app) is FastAPI,
            "instance_is_starlette": isinstance(app, Starlette),
        }

    return app
