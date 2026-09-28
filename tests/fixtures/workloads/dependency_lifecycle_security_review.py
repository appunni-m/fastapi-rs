"""Input-only dependency lifecycle, security-cache, and scope workload."""

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Security, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.security import SecurityScopes


class Session:
    def __init__(self, name: str = "session") -> None:
        self.name = name
        self.open = True


def _stream_json(value: dict[str, Any]):
    yield json.dumps(value, separators=(",", ":")).encode("utf-8")


def create_app() -> FastAPI:
    app = FastAPI()
    events: list[str] = []
    counters = {"security": 0}

    class ClosedSession:
        def __init__(self) -> None:
            self.data = ["cedar", "birch"]
            self.open = False

        def __iter__(self):
            for item in self.data:
                if not self.open:
                    raise ValueError("Session closed")
                yield item

    def broken_session():
        yield ClosedSession()

    @app.get("/broken-session-data")
    def broken_session_data(
        session: Annotated[ClosedSession, Depends(broken_session)],
    ) -> list[str]:
        return list(session)

    def baseline_user(security_scopes: SecurityScopes) -> dict[str, Any]:
        return {"user": "john", "scopes": security_scopes.scopes}

    def original_user(security_scopes: SecurityScopes) -> dict[str, Any]:
        return {"user": "john", "scopes": security_scopes.scopes}

    def replacement_user(security_scopes: SecurityScopes) -> dict[str, Any]:
        return {"user": "alice", "scopes": security_scopes.scopes}

    app.dependency_overrides[original_user] = replacement_user

    @app.get("/security/baseline")
    def security_baseline(
        user: Annotated[dict[str, Any], Security(baseline_user, scopes=["read", "write"])],
    ) -> dict[str, Any]:
        return user

    @app.get("/security/override")
    def security_override(
        user: Annotated[dict[str, Any], Security(original_user, scopes=["read", "write"])],
    ) -> dict[str, Any]:
        return user

    def security_counter() -> int:
        counters["security"] += 1
        return counters["security"]

    @app.get("/security/cache")
    def security_cache(
        direct: Annotated[int, Depends(security_counter)],
        scoped_first: Annotated[int, Security(security_counter, scopes=["scope"])],
        scoped_second: Annotated[int, Security(security_counter, scopes=["scope"])],
    ) -> dict[str, int]:
        return {
            "direct": direct,
            "scoped_first": scoped_first,
            "scoped_second": scoped_second,
        }

    def request_session():
        session = Session("request")
        events.append("request:open")
        try:
            yield session
        finally:
            session.open = False
            events.append("request:close")

    def function_session():
        session = Session("function")
        events.append("function:open")
        try:
            yield session
        finally:
            session.open = False
            events.append("function:close")

    RequestSession = Annotated[Session, Depends(request_session, scope="request")]
    FunctionSession = Annotated[Session, Depends(function_session, scope="function")]

    def named_request_sessions(
        first: RequestSession,
        second: RequestSession,
    ):
        assert first is second
        named = Session("named-request")
        events.append("named-request:open")
        try:
            yield named, second
        finally:
            named.open = False
            events.append("named-request:close")

    def named_function_sessions(session: FunctionSession):
        named = Session("named-function")
        events.append("named-function:open")
        try:
            yield named, session
        finally:
            named.open = False
            events.append("named-function:close")

    def regular_function_sessions(session: FunctionSession) -> tuple[Session, Session]:
        return Session("regular-function"), session

    @app.get("/yield/nested-request")
    def nested_request(
        sessions: Annotated[tuple[Session, Session], Depends(named_request_sessions)],
    ) -> StreamingResponse:
        named, session = sessions
        return StreamingResponse(
            _stream_json({"named_open": named.open, "session_open": session.open}),
            media_type="application/json",
        )

    @app.get("/yield/named-function")
    def named_function(
        sessions: Annotated[
            tuple[Session, Session], Depends(named_function_sessions, scope="function")
        ],
    ) -> StreamingResponse:
        named, session = sessions
        return StreamingResponse(
            _stream_json({"named_open": named.open, "session_open": session.open}),
            media_type="application/json",
        )

    @app.get("/yield/regular-function")
    def regular_function(
        sessions: Annotated[tuple[Session, Session], Depends(regular_function_sessions)],
    ) -> StreamingResponse:
        named, session = sessions
        return StreamingResponse(
            _stream_json({"named_open": named.open, "session_open": session.open}),
            media_type="application/json",
        )

    async def websocket_request_session():
        session = Session("websocket-request")
        events.append("websocket-request:open")
        try:
            yield session
        finally:
            session.open = False
            events.append("websocket-request:close")

    async def websocket_function_session():
        session = Session("websocket-function")
        events.append("websocket-function:open")
        try:
            yield session
        finally:
            session.open = False
            events.append("websocket-function:close")

    WebSocketRequestSession = Annotated[
        Session, Depends(websocket_request_session, scope="request")
    ]
    WebSocketFunctionSession = Annotated[
        Session, Depends(websocket_function_session, scope="function")
    ]

    async def websocket_named_request_sessions(
        first: WebSocketRequestSession,
        second: WebSocketRequestSession,
    ):
        assert first is second
        named = Session("websocket-named-request")
        events.append("websocket-named-request:open")
        try:
            yield named, second
        finally:
            named.open = False
            events.append("websocket-named-request:close")

    async def websocket_named_function_sessions(session: WebSocketFunctionSession):
        named = Session("websocket-named-function")
        events.append("websocket-named-function:open")
        try:
            yield named, session
        finally:
            named.open = False
            events.append("websocket-named-function:close")

    async def websocket_regular_function_sessions(
        session: WebSocketFunctionSession,
    ) -> tuple[Session, Session]:
        return Session("websocket-regular-function"), session

    @app.websocket("/ws/two-scopes")
    async def websocket_two_scopes(
        websocket: WebSocket,
        function_value: WebSocketFunctionSession,
        request_value: WebSocketRequestSession,
    ) -> None:
        await websocket.accept()
        await websocket.send_json(
            {"function_open": function_value.open, "request_open": request_value.open}
        )
        await websocket.close()

    @app.websocket("/ws/sub")
    async def websocket_sub(
        websocket: WebSocket,
        sessions: Annotated[tuple[Session, Session], Depends(websocket_named_request_sessions)],
    ) -> None:
        named, session = sessions
        await websocket.accept()
        await websocket.send_json({"named_open": named.open, "session_open": session.open})
        await websocket.close()

    @app.websocket("/ws/named-function")
    async def websocket_named_function(
        websocket: WebSocket,
        sessions: Annotated[
            tuple[Session, Session],
            Depends(websocket_named_function_sessions, scope="function"),
        ],
    ) -> None:
        named, session = sessions
        await websocket.accept()
        await websocket.send_json({"named_open": named.open, "session_open": session.open})
        await websocket.close()

    @app.websocket("/ws/regular-function")
    async def websocket_regular_function(
        websocket: WebSocket,
        sessions: Annotated[tuple[Session, Session], Depends(websocket_regular_function_sessions)],
    ) -> None:
        named, session = sessions
        await websocket.accept()
        await websocket.send_json({"named_open": named.open, "session_open": session.open})
        await websocket.close()

    def conditional_cleanup(path_suffix: str, scope_name: str):
        def dependency(request: Request):
            yield
            if request.scope["path"].endswith(path_suffix):
                events.append(f"{scope_name}:{path_suffix}:cleanup")
                raise HTTPException(status_code=503, detail="Exception after yield")

        return dependency

    placement_app = FastAPI(
        dependencies=[
            Depends(conditional_cleanup("/app-function", "app-function"), scope="function"),
            Depends(conditional_cleanup("/app-request", "app-request"), scope="request"),
        ]
    )

    @placement_app.get("/app-function")
    def app_function_scope() -> dict[str, str]:
        return {"status": "ok"}

    @placement_app.get("/app-request")
    def app_request_scope() -> dict[str, str]:
        return {"status": "ok"}

    function_router = APIRouter(
        dependencies=[
            Depends(conditional_cleanup("/function/", "router-function"), scope="function")
        ]
    )
    request_router = APIRouter(
        dependencies=[Depends(conditional_cleanup("/request/", "router-request"), scope="request")]
    )

    @function_router.get("/")
    def router_function_scope() -> dict[str, str]:
        return {"status": "ok"}

    @request_router.get("/")
    def router_request_scope() -> dict[str, str]:
        return {"status": "ok"}

    placement_app.include_router(function_router, prefix="/router/function")
    placement_app.include_router(request_router, prefix="/router/request")
    app.mount("/placement", placement_app)

    @app.get("/events")
    def read_events() -> dict[str, list[str]]:
        return {"events": list(events)}

    return app
