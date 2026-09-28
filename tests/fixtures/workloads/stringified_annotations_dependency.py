"""Independent request dependency declared with postponed annotations."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Request


class RequestLabel:
    def __call__(self, request: Request) -> str:
        return f"{request.method.lower()}-context"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/annotations/")
    async def read_annotation(
        label: Annotated[str, Depends(RequestLabel())],
    ) -> dict[str, str]:
        return {"label": label}

    return app
