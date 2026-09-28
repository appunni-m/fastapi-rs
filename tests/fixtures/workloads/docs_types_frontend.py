from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi import Path as PathParameter


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/measure/{count}")
    async def measure(
        count: Annotated[int, PathParameter(gt=0)],
        ratio: Annotated[float, Query(gt=0)],
        enabled: bool = True,
    ) -> dict[str, object]:
        return {"count": count, "ratio": ratio, "enabled": enabled}

    @app.get("/api/health")
    async def frontend_health() -> dict[str, str]:
        return {"state": "api-route"}

    directory = TemporaryDirectory(prefix="fastapi-docs-frontend-")
    frontend_root = Path(directory.name)
    (frontend_root / "index.html").write_text(
        "<!doctype html><title>fixture frontend</title>", encoding="utf-8"
    )
    assets = frontend_root / "assets"
    assets.mkdir()
    (assets / "client.js").write_text("export const fixture = true;", encoding="utf-8")
    app.state.frontend_directory = directory
    app.frontend("/", directory=str(frontend_root), fallback="index.html")
    return app
