"""Input-only lifecycle, streaming, context, and WebSocket dependency routes."""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import StreamingResponse

_request_marker: ContextVar[str | None] = ContextVar("dependency_wave_marker", default=None)


def create_app() -> FastAPI:
    app = FastAPI()
    events: list[str] = []

    @contextmanager
    def open_named_resource(name: str):
        events.append(f"open:{name}")
        try:
            yield {"name": name, "ready": True}
        finally:
            events.append(f"close:{name}")

    def outer_resource():
        with open_named_resource("outer") as resource:
            yield resource

    def inner_resource(outer: Annotated[dict, Depends(outer_resource)]):
        with open_named_resource("inner") as resource:
            yield {"outer": outer, "inner": resource}

    @app.get("/context-stack")
    def context_stack(
        resources: Annotated[dict, Depends(inner_resource)],
    ) -> dict[str, object]:
        return {
            "outer": resources["outer"]["ready"],
            "inner": resources["inner"]["ready"],
        }

    def mapped_failure():
        try:
            yield "prepared"
        except ArithmeticError as error:
            events.append("handled:arithmetic")
            raise HTTPException(status_code=409, detail="operation declined") from error
        finally:
            events.append("closed:mapped")

    @app.get("/mapped-failure")
    def mapped_failure_route(value: Annotated[str, Depends(mapped_failure)]) -> str:
        raise ArithmeticError("discard this operation")

    def failed_teardown():
        yield "ready"
        events.append("close:failed")
        raise RuntimeError("teardown failed after response")

    @app.get("/failed-teardown")
    def failed_teardown_route(value: Annotated[str, Depends(failed_teardown)]) -> dict[str, str]:
        return {"value": value}

    class Inventory:
        def __init__(self) -> None:
            self.open = True
            self.entries = ["elm", "ash", "fir"]

        def __iter__(self):
            for entry in self.entries:
                if not self.open:
                    raise LookupError("inventory is closed")
                yield entry

    def open_inventory():
        inventory = Inventory()
        try:
            yield inventory
        finally:
            inventory.open = False
            events.append("close:inventory")

    def already_closed_inventory():
        inventory = Inventory()
        inventory.open = False
        yield inventory

    @app.get("/stream")
    def stream_inventory(inventory: Annotated[Inventory, Depends(open_inventory)]):
        return StreamingResponse((f"{entry};" for entry in inventory), media_type="text/plain")

    @app.get("/stream-failure")
    def stream_closed_inventory(
        inventory: Annotated[Inventory, Depends(already_closed_inventory)],
    ):
        return StreamingResponse((f"{entry};" for entry in inventory), media_type="text/plain")

    def websocket_inventory():
        inventory = Inventory()
        try:
            yield inventory
        finally:
            inventory.open = False
            events.append("close:websocket-inventory")

    def unavailable_websocket_inventory():
        inventory = Inventory()
        inventory.open = False
        yield inventory

    @app.websocket("/ws/inventory")
    async def websocket_inventory_route(
        websocket: WebSocket,
        inventory: Annotated[Inventory, Depends(websocket_inventory)],
    ) -> None:
        await websocket.accept()
        for entry in inventory:
            await websocket.send_text(entry)
        await websocket.close()

    @app.websocket("/ws/inventory-failure")
    async def websocket_inventory_failure(
        websocket: WebSocket,
        inventory: Annotated[Inventory, Depends(unavailable_websocket_inventory)],
    ) -> None:
        await websocket.accept()
        for entry in inventory:
            await websocket.send_text(entry)
        await websocket.close()

    def scoped_resource():
        state = {"open": True}
        try:
            yield state
        finally:
            state["open"] = False
            events.append("close:scoped-websocket")

    @app.websocket("/ws/function-scope")
    async def function_scope_socket(
        websocket: WebSocket,
        resource: Annotated[dict, Depends(scoped_resource, scope="function")],
    ) -> None:
        await websocket.accept()
        await websocket.send_json({"open_during_handler": resource["open"]})
        await websocket.close()

    @app.websocket("/ws/request-scope")
    async def request_scope_socket(
        websocket: WebSocket,
        resource: Annotated[dict, Depends(scoped_resource, scope="request")],
    ) -> None:
        await websocket.accept()
        await websocket.send_json({"open_during_handler": resource["open"]})
        await websocket.close()

    async def context_dependency():
        marker = "cedar"
        token = _request_marker.set(marker)
        try:
            yield marker
        finally:
            _request_marker.reset(token)
            events.append("reset:context")

    @app.middleware("http")
    async def add_context_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["x-context-layer"] = "present"
        return response

    @app.get("/contextvar")
    def contextvar_route(
        marker: Annotated[str, Depends(context_dependency)],
    ) -> dict[str, str | None]:
        return {"dependency": marker, "current": _request_marker.get()}

    @app.get("/events")
    def read_events() -> dict[str, list[str]]:
        return {"events": list(events)}

    return app
