"""Input workload for the FastAPI status-module re-export contract."""

import warnings

from fastapi import FastAPI, status
from starlette import status as starlette_status


def _deprecated_status_attribute(name: str) -> dict[str, object]:
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        value = getattr(status, name)

    return {
        "value": value,
        "warnings": [
            {
                "category": f"{record.category.__module__}.{record.category.__qualname__}",
                "filename": record.filename,
                "line": record.lineno,
                "message": str(record.message),
            }
            for record in records
        ],
    }


def _unknown_status_attribute() -> dict[str, object]:
    unknown_name = "FASTAPI_RS_UNKNOWN_STATUS_MEMBER"
    try:
        value = getattr(status, unknown_name)
    except Exception as error:
        return {
            "exception_class": f"{type(error).__module__}.{type(error).__qualname__}",
            "exception_args": list(error.args),
        }
    return {"value": value}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/status")
    def read_status_namespace() -> dict[str, object]:
        directory = dir(status)
        exported_names = list(status.__all__)
        deprecated_names = sorted(set(directory).difference(exported_names))
        return {
            "module_identity_matches": status is starlette_status,
            "public_names": exported_names,
            "exports": {name: getattr(status, name) for name in sorted(exported_names)},
            "directory": directory,
            "deprecated": {name: _deprecated_status_attribute(name) for name in deprecated_names},
            "unknown_attribute": _unknown_status_attribute(),
        }

    return app
