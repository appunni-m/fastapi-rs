"""Independent multipart inputs for the middleware exception boundary."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile


class IncomingBodyQuotaMiddleware:
    def __init__(self, app: Any, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        received_bytes = 0

        async def quota_receive() -> Any:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_bytes:
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "name": "UploadBudgetExceeded",
                            "code": 734,
                            "message": "Multipart body exceeds the configured budget",
                        },
                    )
            return message

        await self.app(scope, quota_receive, send)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(IncomingBodyQuotaMiddleware, max_bytes=256)

    router = APIRouter()

    @router.post("/attachments")
    async def store_attachment(
        upload: Annotated[UploadFile, File()],
    ) -> dict[str, str]:
        return {"stored_as": upload.filename or "unnamed"}

    app.include_router(router)
    return app
