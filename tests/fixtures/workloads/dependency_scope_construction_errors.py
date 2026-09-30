"""Input-only route-construction workload for dependency scope validation."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI
from starlette.websockets import WebSocket


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    """Register one HTTP or WebSocket route with an invalid yielded scope graph."""
    del event_trace
    app = FastAPI()

    def function_session():
        yield object()

    def request_session(
        session: Annotated[Any, Depends(function_session, scope="function")],
    ):
        yield session

    route_kind = factory_input["route_kind"]
    if route_kind == "http":

        @app.get("/invalid-scope")
        def invalid_http_route(
            session: Annotated[Any, Depends(request_session)],
        ) -> None:
            del session

    elif route_kind == "websocket":

        @app.websocket("/invalid-scope")
        async def invalid_websocket_route(
            websocket: WebSocket,
            session: Annotated[Any, Depends(request_session)],
        ) -> None:
            del websocket, session

    else:
        raise ValueError("unsupported route kind in workload input")

    return app
