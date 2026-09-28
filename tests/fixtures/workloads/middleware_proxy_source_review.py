"""Independent ASGI workloads for middleware and proxy source review."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one independently parameterized application per recipe case."""
    del event_trace
    scenario = factory_input["scenario"]

    if scenario == "https-redirect":
        app = FastAPI()
        app.add_middleware(HTTPSRedirectMiddleware)

        @app.get("/")
        async def status() -> dict[str, str]:
            return {"state": "secure"}

        return app

    if scenario == "trusted-host":
        app = FastAPI()
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["example.net", "*.example.net"],
        )

        @app.get("/status")
        async def status() -> dict[str, str]:
            return {"state": "accepted"}

        return app

    if scenario == "gzip":
        app = FastAPI()
        app.add_middleware(GZipMiddleware, minimum_size=256, compresslevel=5)
        payload = str(factory_input["fill"]) * int(factory_input["repeat"])

        @app.get("/compressed")
        async def compressed() -> PlainTextResponse:
            return PlainTextResponse(payload)

        @app.get("/status")
        async def status() -> dict[str, str]:
            return {"state": "ready"}

        return app

    if scenario == "proxy-root-path":
        app_options: dict[str, Any] = {"root_path": str(factory_input["app_root_path"])}
        if "servers" in factory_input:
            app_options["servers"] = list(factory_input["servers"])
        if "root_path_in_servers" in factory_input:
            app_options["root_path_in_servers"] = bool(factory_input["root_path_in_servers"])
        app = FastAPI(**app_options)
        message = str(factory_input["message"])

        @app.get("/service")
        def service(request: Request) -> dict[str, str | None]:
            return {"message": message, "root_path": request.scope.get("root_path")}

        return app

    if scenario == "decorator-middleware":
        app = FastAPI()
        marker = str(factory_input["process_time_marker"])

        @app.middleware("http")
        async def add_process_marker(request: Request, call_next: Any) -> Any:
            response = await call_next(request)
            response.headers["X-Process-Time"] = marker
            return response

        return app

    if scenario == "static-files":
        temporary_directory = tempfile.TemporaryDirectory(prefix="fastapi-rs-static-review-")
        static_directory = Path(temporary_directory.name)
        (static_directory / str(factory_input["file_name"])).write_text(
            str(factory_input["file_body"]), encoding="utf-8"
        )

        app = FastAPI()
        app.mount(
            "/assets",
            StaticFiles(directory=static_directory),
            name="assets",
        )
        app.state.source_review_temporary_directory = temporary_directory
        return app

    if scenario == "dependency-override":
        app = FastAPI()
        default_profile = dict(factory_input["default_profile"])
        overridden_profile = dict(factory_input["overridden_profile"])

        def get_profile() -> dict[str, Any]:
            return default_profile

        def override_profile() -> dict[str, Any]:
            return overridden_profile

        app.dependency_overrides[get_profile] = override_profile

        @app.get("/profile")
        async def profile(settings: dict[str, Any] = Depends(get_profile)) -> dict[str, Any]:  # noqa: B008
            return settings

        return app

    raise ValueError(f"unknown source-review workload scenario: {scenario}")
