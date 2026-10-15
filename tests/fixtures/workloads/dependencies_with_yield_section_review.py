"""Input-only baseline for yielded dependency values and teardown."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    del factory_input
    app = FastAPI()
    events = event_trace

    async def get_session():
        session = {"open": True}
        events.append("opened")
        try:
            yield session
        except LookupError as error:
            events.append(f"caught:{error.args[0]}")
            raise
        finally:
            session["open"] = False
            events.append("closed")

    @app.get("/database-session")
    def database_session(
        session: Annotated[dict[str, bool], Depends(get_session)],
    ) -> dict[str, bool]:
        return {"open": session["open"]}

    @app.get("/session-events")
    def session_events() -> dict[str, list[str]]:
        return {"events": list(events)}

    @app.get("/try-error")
    def try_error(
        _session: Annotated[dict[str, bool], Depends(get_session)],
    ) -> None:
        raise LookupError("endpoint failure")

    return app
