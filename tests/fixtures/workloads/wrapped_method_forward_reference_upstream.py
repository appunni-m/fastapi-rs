"""Independent HTTP stimuli for wrapped methods with imported forward references."""

from __future__ import annotations

import functools
import importlib
import sys
from types import ModuleType

from fastapi import FastAPI
from pydantic import BaseModel


def _import_forwardref_method():
    module_name = f"{__name__}.forward_reference_type"
    helper_module = ModuleType(module_name)
    helper_module.BaseModel = BaseModel
    sys.modules[module_name] = helper_module
    exec(
        compile(
            "class ForwardRefModel(BaseModel):\n"
            "    x: int = 0\n"
            "\n"
            "def forwardref_method(input: 'ForwardRefModel') -> 'ForwardRefModel':\n"
            "    return ForwardRefModel(x=input.x + 1)\n",
            module_name,
            "exec",
        ),
        helper_module.__dict__,
    )
    imported_module = importlib.import_module(module_name)
    return imported_module.forwardref_method


def _passthrough(function):
    @functools.wraps(function)
    def method(*args, **kwargs):
        return function(*args, **kwargs)

    return method


def create_app() -> FastAPI:
    app = FastAPI()
    forwardref_method = _import_forwardref_method()
    app.post("/endpoint")(_passthrough(forwardref_method))
    app.post("/endpoint2")(_passthrough(_passthrough(forwardref_method)))
    return app
