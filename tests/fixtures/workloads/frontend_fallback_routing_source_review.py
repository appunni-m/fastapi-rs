"""Independent ASGI stimuli for FastAPI frontend fallback and route policy."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request

_DEFERRED_MISSING_DIRECTORY = "tests/fixtures/workloads/.fastapi-frontend-review-missing-directory"


def _keep_directory(app: FastAPI, files: dict[str, str]) -> str:
    directory = TemporaryDirectory(prefix="fastapi-frontend-review-")
    root = Path(directory.name)
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    directories = getattr(app.state, "frontend_review_directories", None)
    if directories is None:
        directories = []
        app.state.frontend_review_directories = directories
    directories.append(directory)
    return directory.name


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Construct an app from one input-only frontend scenario."""
    del event_trace
    scenario = factory_input["scenario"]

    if scenario == "fallback-routing-surface":
        app = FastAPI()

        automatic_404 = _keep_directory(
            app,
            {"index.html": "auto app shell", "404.html": "auto not found"},
        )
        app.frontend("/auto", directory=automatic_404)

        automatic_index = _keep_directory(app, {"index.html": "auto index shell"})
        app.frontend("/auto-index", directory=automatic_index)

        automatic_empty = _keep_directory(app, {})
        app.frontend("/auto-empty", directory=automatic_empty)

        explicit_index = _keep_directory(app, {"index.html": "explicit app shell"})
        app.frontend("/spa", directory=explicit_index, fallback="index.html")

        disabled = _keep_directory(app, {"index.html": "disabled app shell"})
        app.frontend("/none", directory=disabled, fallback=None)

        root = _keep_directory(
            app,
            {
                "index.html": "root app shell",
                "api/users": "static file at the API path",
            },
        )

        api_router = APIRouter()

        @api_router.get("/api/users")
        def read_users() -> dict[str, str]:
            return {"source": "api route"}

        @api_router.get("/api/missing")
        def missing_api() -> None:
            raise HTTPException(status_code=404, detail="api-owned missing route")

        app.include_router(api_router)
        app.frontend("/", directory=root, fallback="index.html")

        def require_session(request: Request) -> None:
            if request.cookies.get("session") != "ok":
                raise HTTPException(status_code=401)

        dependency_files = _keep_directory(
            app,
            {"index.html": "authenticated app shell", "asset.txt": "authenticated asset"},
        )
        dependency_router = APIRouter(dependencies=[Depends(require_session)])
        dependency_router.frontend("/", directory=dependency_files, fallback="index.html")
        app.include_router(dependency_router, prefix="/app")

        router_files = _keep_directory(app, {"asset.txt": "router asset"})
        router = APIRouter(prefix="/internal")
        router.frontend("/ui", directory=router_files, fallback=None)
        app.include_router(router, prefix="/prefix")
        return app

    if scenario == "check-dir-auto-production":
        app = FastAPI()
        previous = os.environ.get("FASTAPI_ENV")
        os.environ["FASTAPI_ENV"] = "production"
        try:
            app.frontend("/", directory=_DEFERRED_MISSING_DIRECTORY)
        finally:
            if previous is None:
                os.environ.pop("FASTAPI_ENV", None)
            else:
                os.environ["FASTAPI_ENV"] = previous
        return app

    if scenario == "explicit-fallback-file-missing":
        app = FastAPI()
        previous = os.environ.get("FASTAPI_ENV")
        os.environ["FASTAPI_ENV"] = "production"
        try:
            app.frontend(
                "/",
                directory="tests/fixtures/workloads",
                fallback="index.html",
            )
        finally:
            if previous is None:
                os.environ.pop("FASTAPI_ENV", None)
            else:
                os.environ["FASTAPI_ENV"] = previous
        return app

    if scenario == "invalid-fallback-configuration":
        app = FastAPI()
        directory = _keep_directory(app, {})
        app.frontend("/", directory=directory, fallback="not-a-fallback")  # type: ignore[arg-type]
        return app

    if scenario == "check-dir-false-deferred-error":
        app = FastAPI()
        app.frontend(
            "/",
            directory=_DEFERRED_MISSING_DIRECTORY,
            fallback=None,
            check_dir=False,
        )
        return app

    raise ValueError("unknown frontend source-review scenario")
