"""Input-driven cases for public dependency and parameter model behavior."""

from __future__ import annotations

from fastapi import Depends, FastAPI, Security
from fastapi.openapi.models import Schema
from fastapi.params import Body, Cookie, Header, Param, Path, Query


def _dependency_marker() -> str:
    return "marker"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/dependency-key-hashes")
    def dependency_key_hashes() -> dict[str, bool]:
        first = Depends(_dependency_marker)
        equivalent = Depends(_dependency_marker)
        function_scoped = Depends(_dependency_marker, scope="function")
        same_function_scope = Depends(_dependency_marker, scope="function")
        secured = Security(_dependency_marker)
        equivalent_security = Security(_dependency_marker)
        return {
            "same_dependency_hash": hash(first) == hash(equivalent),
            "scope_changes_hash": hash(first) != hash(function_scoped),
            "same_scoped_hash": hash(function_scoped) == hash(same_function_scope),
            "same_security_hash": hash(secured) == hash(equivalent_security),
        }

    @app.post("/schema-type")
    async def schema_type(payload: dict[str, object]) -> dict[str, object]:
        try:
            schema = Schema(type=payload.get("type"))
        except ValueError as exc:
            return {
                "error_class": f"{type(exc).__module__}.{type(exc).__qualname__}",
                "error_message": str(exc),
            }
        return {"schema_type": schema.type}

    @app.get("/parameter-representations")
    def parameter_representations() -> dict[str, list[str]]:
        values: list[object] = ["harbor-tag", None, ..., 29, ["bronze"]]
        parameter_types = (Param, Query, Header, Cookie, Body)
        result = {
            parameter_type.__name__: [repr(parameter_type(value)) for value in values]
            for parameter_type in parameter_types
        }
        result["Path"] = [repr(Path()), repr(Path(...))]
        return result

    return app
