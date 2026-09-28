"""FastAPI frontend route metadata with an isolated deterministic asset."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI

_ASSET_DIRS: list[TemporaryDirectory[str]] = []


def create_app() -> FastAPI:
    asset_dir = TemporaryDirectory(prefix="fastapi-rs-frontend-")
    _ASSET_DIRS.append(asset_dir)
    Path(asset_dir.name, "index.html").write_text("client bundle", encoding="utf-8")

    app = FastAPI()

    @app.get("/api")
    def read_api() -> dict[str, bool]:
        return {"ok": True}

    app.frontend("/", directory=asset_dir.name, fallback="index.html")
    return app
