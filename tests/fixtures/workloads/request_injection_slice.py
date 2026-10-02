"""Input workload for direct Request injection and cached body reads."""

from fastapi import Depends, FastAPI, Request
from fastapi.requests import Request as RequestsModuleRequest
from pydantic import BaseModel


class Payload(BaseModel):
    message: str


async def read_body(request: Request) -> str:
    return (await request.body()).decode("utf-8")


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.request_marker = "request-app-state"

    @app.post("/raw-body/{item_id}")
    async def raw_body(item_id: str, request: Request) -> dict[str, object]:
        return {
            "body": (await request.body()).decode("utf-8"),
            "item_id": request.path_params["item_id"],
            "is_request_class": type(request) is Request,
            "root_and_module_aliases_match": Request is RequestsModuleRequest,
        }

    @app.post("/parsed-body")
    async def parsed_body(payload: Payload, request: Request) -> dict[str, object]:
        return {
            "body": (await request.body()).decode("utf-8"),
            "message": payload.message,
            "is_request_class": type(request) is Request,
            "root_and_module_aliases_match": Request is RequestsModuleRequest,
        }

    @app.get("/request-app-state")
    async def request_app_state(request: Request) -> dict[str, object]:
        return {
            "state": request.app.state.request_marker,
            "is_scope_app": request.app is request.scope["app"],
        }

    @app.post("/dependency-body")
    async def dependency_body(body: str = Depends(read_body)) -> dict[str, str]:
        return {"body": body}

    return app
