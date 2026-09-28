"""Independent yielded-resource failure workload for the WebSocket contract."""

from __future__ import annotations

from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, WebSocket


class Session:
    def __init__(self) -> None:
        self._entries = ("foo", "bar", "baz")
        self._open = True

    def close(self) -> None:
        self._open = False

    def __iter__(self) -> Iterator[str]:
        for entry in self._entries:
            if not self._open:
                raise ValueError("Session closed")
            yield entry


@contextmanager
def session_lease() -> Generator[Session, None, None]:
    session = Session()
    try:
        yield session
    finally:
        session.close()


def closed_session() -> Generator[Session, None, None]:
    with session_lease() as session:
        session.close()
        yield session


ClosedSession = Annotated[Session, Depends(closed_session)]


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.websocket("/ws-broken")
    async def stream_session(websocket: WebSocket, session: ClosedSession) -> None:
        await websocket.accept()
        for entry in session:
            await websocket.send_text(entry)

    return app
