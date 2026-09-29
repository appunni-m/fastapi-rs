"""Independent workloads for tutorial yield and context-manager dependencies."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI


class _Resource:
    def __init__(self, name: str, events: list[str]) -> None:
        self.name = name
        self.events = events

    def close(self, parent: _Resource | None = None) -> None:
        suffix = f":{parent.name}" if parent is not None else ""
        self.events.append(f"close:{self.name}{suffix}")

    def __str__(self) -> str:
        return self.name


class _Session:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def close(self) -> None:
        self.events.append("session-close")

    def __str__(self) -> str:
        return "db-session"


class _SessionContext:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.db = _Session(events)

    def __enter__(self) -> _Session:
        self.events.append("context-enter")
        return self.db

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.events.append("context-exit")
        self.db.close()


_events: list[str] = []


async def dependency_a():
    resource = _Resource("a", _events)
    _events.append("open:a")
    try:
        yield resource
    finally:
        resource.close()


dependency_a_parameter = Depends(dependency_a)


async def dependency_b_default(dep_a=dependency_a_parameter):
    resource = _Resource("b", _events)
    _events.append("open:b")
    try:
        yield resource
    finally:
        resource.close(dep_a)


dependency_b_parameter = Depends(dependency_b_default)


async def dependency_c_default(dep_b=dependency_b_parameter):
    resource = _Resource("c", _events)
    _events.append("open:c")
    try:
        yield resource
    finally:
        resource.close(dep_b)


async def get_db():
    with _SessionContext(_events) as db:
        yield db


def create_app() -> FastAPI:
    global _events
    _events = []
    app = FastAPI()

    @app.get("/yield-chain/default")
    def read_default(c: Annotated[Any, Depends(dependency_c_default)]):
        return {"c": str(c)}

    @app.get("/context-manager")
    def read_context_manager(c: Annotated[Any, Depends(get_db)]):
        return {"c": str(c)}

    @app.get("/events")
    def read_events():
        return {"events": list(_events)}

    return app
