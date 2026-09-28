"""Independent ASGI stimuli for status precedence on streamed responses."""

from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import Depends, FastAPI, Response
from fastapi.responses import EventSourceResponse, StreamingResponse


def create_app() -> FastAPI:
    app = FastAPI()

    def set_accepted(response: Response) -> None:
        response.status_code = 202

    @app.post("/sse", response_class=EventSourceResponse, status_code=201)
    async def sse() -> AsyncIterable[dict[str, str]]:
        yield {"message": "created"}

    @app.post("/jsonl", status_code=201)
    async def jsonl() -> AsyncIterable[dict[str, str]]:
        yield {"message": "created"}

    @app.post("/raw", response_class=StreamingResponse, status_code=201)
    async def raw() -> AsyncIterable[str]:
        yield "accepted"

    @app.post("/sse-dependency", response_class=EventSourceResponse, responses={202: {}})
    async def sse_dependency(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[dict[str, str]]:
        yield {"message": "accepted"}

    @app.post("/jsonl-dependency", responses={202: {}})
    async def jsonl_dependency(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[dict[str, str]]:
        yield {"message": "accepted"}

    @app.post("/raw-dependency", response_class=StreamingResponse, responses={202: {}})
    async def raw_dependency(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[str]:
        yield "accepted"

    @app.post(
        "/sse-dependency-override",
        response_class=EventSourceResponse,
        status_code=201,
        responses={202: {}},
    )
    async def sse_dependency_override(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[dict[str, str]]:
        yield {"message": "overridden"}

    @app.post("/jsonl-dependency-override", status_code=201, responses={202: {}})
    async def jsonl_dependency_override(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[dict[str, str]]:
        yield {"message": "overridden"}

    @app.post(
        "/raw-dependency-override",
        response_class=StreamingResponse,
        status_code=201,
        responses={202: {}},
    )
    async def raw_dependency_override(
        accepted: Annotated[None, Depends(set_accepted)],
    ) -> AsyncIterable[str]:
        yield "overridden"

    return app
