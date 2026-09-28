"""Independent route-construction workload for multipart installation guards."""

import importlib
import warnings
from types import ModuleType
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile

_MISSING = object()


def _set_version(module: ModuleType, attribute: str, value: str) -> tuple[ModuleType, str, Any]:
    previous = getattr(module, attribute)
    setattr(module, attribute, value)
    return module, attribute, previous


def _delete_attribute(
    module: ModuleType,
    attribute: str,
) -> tuple[ModuleType, str, Any]:
    previous = getattr(module, attribute, _MISSING)
    if previous is not _MISSING:
        delattr(module, attribute)
    return module, attribute, previous


def _restore(patches: list[tuple[ModuleType, str, Any]]) -> None:
    for module, attribute, previous in reversed(patches):
        if previous is _MISSING:
            if hasattr(module, attribute):
                delattr(module, attribute)
        else:
            setattr(module, attribute, previous)


def _endpoint(shape: str) -> Any:
    if shape == "form-username":

        async def root(username: str = Form()):
            return username

    elif shape == "file-upload":

        async def root(f: UploadFile = File()):  # noqa: B008
            return f

    elif shape == "file-bytes":

        async def root(f: bytes = File()):
            return f

    elif shape == "multi-form":

        async def root(username: str = Form(), password: str = Form()):
            return username

    elif shape == "form-file":

        async def root(username: str = Form(), f: UploadFile = File()):  # noqa: B008
            return username

    else:
        raise ValueError("unsupported multipart route shape in workload input")
    return root


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Apply a per-case package-state mutation, then register one upstream route."""
    del event_trace
    patches: list[tuple[ModuleType, str, Any]] = []
    try:
        package_version = importlib.import_module("python_multipart")
        patches.append(_set_version(package_version, "__version__", "0.0.12"))
        mutation = factory_input["module_mutation"]

        if mutation == "remove-parser":
            multipart_module = importlib.import_module("multipart.multipart")
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                patches.append(_delete_attribute(multipart_module, "parse_options_header"))
            app = FastAPI()
            endpoint = _endpoint(factory_input["route_shape"])
            app.post("/")(endpoint)
        elif mutation == "remove-version":
            multipart_package = importlib.import_module("multipart")
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                patches.append(_delete_attribute(multipart_package, "__version__"))
                app = FastAPI()
                endpoint = _endpoint(factory_input["route_shape"])
                app.post("/")(endpoint)
        elif mutation != "old-python-multipart-version":
            raise ValueError("unsupported multipart module mutation in workload input")
        else:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                app = FastAPI()
                endpoint = _endpoint(factory_input["route_shape"])
                app.post("/")(endpoint)
        return app
    finally:
        _restore(patches)
