"""Independent FastAPI middleware integration workload."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import PlainTextResponse


class BodyLimitMiddleware:
    """Raise FastAPI's HTTP exception when a request body exceeds a limit."""

    def __init__(self, app: Any, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        received_bytes = 0

        async def limited_receive() -> dict[str, Any]:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_body_bytes:
                    raise HTTPException(status_code=413, detail="request body too large")
            return message

        await self.app(scope, limited_receive, send)


def create_app() -> FastAPI:
    app = FastAPI(title="Middleware Contract", version="1.0.0")

    app.add_middleware(BodyLimitMiddleware, max_body_bytes=4)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com"],
    )
    app.add_middleware(HTTPSRedirectMiddleware)

    @app.middleware("http")
    async def mark_response(request: Request, call_next: Any) -> Any:
        if request.url.path == "/body-replay":
            await request.body()
        response = await call_next(request)
        response.headers["X-FastAPI-Middleware"] = "active"
        return response

    @app.get("/status")
    async def status() -> dict[str, str]:
        return {"state": "ready"}

    @app.post("/echo")
    async def echo(request: Request) -> PlainTextResponse:
        body = await request.body()
        return PlainTextResponse(body.decode("utf-8"))

    @app.post("/body-replay")
    async def body_replay(request: Request) -> PlainTextResponse:
        body = await request.body()
        return PlainTextResponse(body.decode("utf-8"))

    return app
