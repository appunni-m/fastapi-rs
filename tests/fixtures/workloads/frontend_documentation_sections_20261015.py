"""Input apps for reviewed FastAPI frontend documentation sections."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import FastAPI

_MISSING_DIRECTORY = "tests/fixtures/workloads/.fastapi-frontend-docs-section-missing-20261015"


def _set_fastapi_env(value: str | None) -> str | None:
    previous = os.environ.get("FASTAPI_ENV")
    if value is None:
        os.environ.pop("FASTAPI_ENV", None)
    else:
        os.environ["FASTAPI_ENV"] = value
    return previous


def _restore_fastapi_env(previous: str | None) -> None:
    if previous is None:
        os.environ.pop("FASTAPI_ENV", None)
    else:
        os.environ["FASTAPI_ENV"] = previous


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Construct one app from a section-specific input case."""
    del event_trace
    scenario = factory_input["scenario"]
    app = FastAPI()

    if scenario == "static-app-asset":
        directory = TemporaryDirectory(prefix="fastapi-frontend-docs-static-")
        root = Path(directory.name)
        assets = root / "assets"
        assets.mkdir()
        (assets / "app.js").write_text("export const built = true;", encoding="utf-8")
        app.state.frontend_docs_directory = directory
        app.frontend("/", directory=str(root))
        return app

    if scenario == "explicit-custom-404":
        directory = TemporaryDirectory(prefix="fastapi-frontend-docs-404-")
        root = Path(directory.name)
        (root / "index.html").write_text("built app shell", encoding="utf-8")
        (root / "404.html").write_text("built page not found", encoding="utf-8")
        app.state.frontend_docs_directory = directory
        app.frontend("/", directory=str(root), fallback="404.html")
        return app

    if scenario == "auto-directory-production-error":
        previous = _set_fastapi_env("production")
        try:
            app.frontend("/", directory=_MISSING_DIRECTORY)
        finally:
            _restore_fastapi_env(previous)
        return app

    if scenario == "auto-directory-development-warning":
        previous = _set_fastapi_env("development")
        try:
            app.frontend("/", directory=_MISSING_DIRECTORY)
        finally:
            _restore_fastapi_env(previous)
        return app

    if scenario == "explicit-check-dir-true":
        app.frontend("/", directory=_MISSING_DIRECTORY, check_dir=True)
        return app

    if scenario == "check-dir-false-defers-error":
        app.frontend("/", directory=_MISSING_DIRECTORY, check_dir=False)
        return app

    raise ValueError(f"unknown frontend documentation scenario: {scenario}")
