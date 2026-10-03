"""Input-only ASGI workload for FastAPI frontend dependency behavior."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response

_FIXED_MTIME_NS = 1_700_000_000_000_000_000


def _frontend_directory(app: FastAPI, files: dict[str, str]) -> str:
    temporary_directory = TemporaryDirectory(prefix="fastapi-frontend-dependencies-")
    root = Path(temporary_directory.name)
    for relative_path, contents in files.items():
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(contents, encoding="utf-8")
        os.utime(file_path, ns=(_FIXED_MTIME_NS, _FIXED_MTIME_NS))
    directories = getattr(app.state, "frontend_dependency_directories", None)
    if directories is None:
        directories = []
        app.state.frontend_dependency_directories = directories
    directories.append(temporary_directory)
    return temporary_directory.name


def _record_dependency(calls: list[str], name: str):
    def dependency(response: Response) -> None:
        calls.append(name)
        response.headers["X-Frontend-Dependency-Order"] = ",".join(calls)

    return dependency


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one fresh app for the selected dependency scenario."""
    del event_trace
    scenario = factory_input["scenario"]

    if scenario == "nested-inclusion-order":
        calls: list[str] = []
        app = FastAPI(dependencies=[Depends(_record_dependency(calls, "app"))])
        directory = _frontend_directory(app, {"index.html": "frontend"})
        child = APIRouter(dependencies=[Depends(_record_dependency(calls, "child"))])
        child.frontend("/ui", directory=directory)
        parent = APIRouter(dependencies=[Depends(_record_dependency(calls, "parent"))])
        parent.include_router(
            child,
            prefix="/child",
            dependencies=[Depends(_record_dependency(calls, "parent-include"))],
        )
        app.include_router(
            parent,
            prefix="/parent",
            dependencies=[Depends(_record_dependency(calls, "app-include"))],
        )
        return app

    if scenario == "dependency-override":

        def require_override() -> None:
            raise HTTPException(status_code=401)

        def allow_override(response: Response) -> None:
            response.headers["X-Frontend-Dependency-Override"] = "applied"

        app = FastAPI(dependencies=[Depends(require_override)])
        app.dependency_overrides[require_override] = allow_override
        directory = _frontend_directory(app, {"index.html": "frontend"})
        app.frontend("/", directory=directory)
        return app

    if scenario == "validation-422":

        def require_token(token: str) -> None:
            del token

        app = FastAPI(dependencies=[Depends(require_token)])
        directory = _frontend_directory(app, {"index.html": "frontend"})
        app.frontend("/", directory=directory)
        return app

    if scenario == "api-route-wins":

        def reject_if_frontend_selected() -> None:
            raise HTTPException(status_code=418, detail="frontend dependency ran")

        app = FastAPI()
        directory = _frontend_directory(
            app,
            {"api": "frontend file must lose to the API route"},
        )
        router = APIRouter(dependencies=[Depends(reject_if_frontend_selected)])
        router.frontend("/", directory=directory)

        @app.get("/api")
        def read_api() -> dict[str, str]:
            return {"source": "api"}

        app.include_router(router)
        return app

    raise ValueError("unknown frontend dependency scenario")
