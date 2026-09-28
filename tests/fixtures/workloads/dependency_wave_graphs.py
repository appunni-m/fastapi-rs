"""Input-only dependency graph, security, response injection, and schema routes."""

from typing import Annotated

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    Response,
    Security,
)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel


def create_app() -> FastAPI:
    app = FastAPI()
    background_log: list[str] = []
    calls = {"store": 0, "identity": 0, "summary": 0, "items": 0}

    class Parcel(BaseModel):
        code: str

    def receive_parcel(parcel: Parcel) -> Parcel:
        return parcel

    def nest_parcels(parcel: Parcel, nested: Annotated[Parcel, Depends(receive_parcel)]):
        return {"base": parcel, "nested": nested}

    @app.post("/parcels/reused")
    def reused_parcel(
        parcel: Parcel,
        again: Annotated[Parcel, Depends(receive_parcel)],
    ) -> list[Parcel]:
        return [parcel, again]

    @app.post("/parcels/nested")
    def nested_parcel(
        parcel: Parcel,
        chain: Annotated[dict, Depends(nest_parcels)],
    ) -> dict[str, object]:
        return {"parcel": parcel, "chain": chain}

    def receive_separate(parcel: Parcel) -> Parcel:
        return parcel

    @app.post("/parcels/separate")
    def separate_parcels(
        first: Parcel,
        second: Annotated[Parcel, Depends(receive_separate)],
    ) -> list[Parcel]:
        return [first, second]

    def tenant_header(*, workspace: str = Header()):
        return workspace

    def labeled_tenant(*, workspace: Annotated[str, Depends(tenant_header)]):
        return f"workspace:{workspace}"

    @app.get("/workspace")
    def workspace(
        direct: Annotated[str, Depends(tenant_header)],
        indirect: Annotated[str, Depends(labeled_tenant)],
    ) -> dict[str, str]:
        return {"direct": direct, "indirect": indirect}

    bearer = OAuth2PasswordBearer(
        tokenUrl="session-token",
        scopes={"view": "Read workspace data", "edit": "Change workspace data"},
    )

    def require_workspace(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(bearer)],
    ) -> dict[str, object]:
        if "view" not in security_scopes.scopes:
            raise HTTPException(status_code=401, detail="view scope required")
        return {"token": token, "scopes": security_scopes.scopes}

    @app.get("/auth/credential")
    def credential(
        grant: Annotated[dict, Security(require_workspace, scopes=["view", "edit"])],
    ) -> dict[str, object]:
        return grant

    @app.get("/auth/parameterless", dependencies=[Security(require_workspace, scopes=["view"])])
    def parameterless_authorized() -> dict[str, str]:
        return {"status": "allowed"}

    @app.get("/auth/no-scopes", dependencies=[Security(require_workspace)])
    def parameterless_without_scope() -> dict[str, str]:
        return {"status": "not reached"}

    def standard_rows() -> list[int]:
        return [2, 4, 6]

    def substitute_rows() -> list[int]:
        return [5, 7, 9]

    @app.get("/overrides/rows")
    def overridden_rows(rows: Annotated[list[int], Depends(standard_rows)]) -> list[int]:
        return rows

    app.dependency_overrides[standard_rows] = substitute_rows

    def identify(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(bearer)],
    ) -> dict[str, object]:
        return {"user": "base-user", "scopes": security_scopes.scopes, "token": token}

    def replacement_identity() -> dict[str, str]:
        return {"user": "alternate-user"}

    @app.get("/overrides/identity")
    def overridden_identity(
        user: Annotated[dict, Security(identify, scopes=["view"])],
    ) -> dict[str, object]:
        return user

    app.dependency_overrides[identify] = replacement_identity

    def get_store() -> str:
        calls["store"] += 1
        return f"store-{calls['store']}"

    def get_identity(
        security_scopes: SecurityScopes,
        store: Annotated[str, Depends(get_store)],
    ) -> dict[str, object]:
        calls["identity"] += 1
        return {
            "member": f"member-{calls['identity']}",
            "scopes": security_scopes.scopes,
            "store": store,
        }

    def get_summary(
        identity: Annotated[dict, Security(get_identity, scopes=["summary"])],
    ) -> dict[str, object]:
        calls["summary"] += 1
        return {"summary_number": calls["summary"], "identity": identity}

    def get_items(
        summary: Annotated[dict, Depends(get_summary)],
    ) -> dict[str, object]:
        calls["items"] += 1
        return {"items_number": calls["items"], "summary": summary}

    @app.get("/scope-graph")
    def scope_graph(
        summary: Annotated[dict, Depends(get_summary)],
        items: Annotated[dict, Security(get_items, scopes=["items"])],
    ) -> dict[str, object]:
        return {"summary": summary, "items": items, "calls": dict(calls)}

    def decorate_response(response: Response) -> Response:
        response.headers["x-layer-one"] = "one"
        return response

    def add_second_layer(
        response: Annotated[Response, Depends(decorate_response)],
    ) -> Response:
        response.headers["x-layer-two"] = "two"
        return response

    @app.get("/response/chain")
    def response_chain(
        response: Annotated[Response, Depends(add_second_layer)],
    ) -> dict[str, str]:
        return {"result": "chain"}

    def choose_response() -> Response:
        response = JSONResponse({"result": "selected"})
        response.headers["x-choice"] = "initial"
        return response

    @app.get("/response/selected")
    def selected_response(
        response: Annotated[Response, Depends(choose_response)],
    ) -> Response:
        response.headers["x-choice"] = "updated"
        return response

    def request_summary(request: Request) -> dict[str, str]:
        return {
            "path": request.url.path,
            "agent": request.headers.get("user-agent", "unset"),
        }

    @app.get("/response/request")
    def request_in_dependency(
        summary: Annotated[dict[str, str], Depends(request_summary)],
    ) -> dict[str, str]:
        return summary

    def schedule_from_dependency(tasks: BackgroundTasks) -> BackgroundTasks:
        tasks.add_task(background_log.append, "dependency")
        return tasks

    @app.get("/response/background")
    def response_background(
        tasks: Annotated[BackgroundTasks, Depends(schedule_from_dependency)],
    ) -> dict[str, bool]:
        tasks.add_task(background_log.append, "endpoint")
        return {"accepted": True}

    @app.get("/response/background-log")
    def read_background_log() -> dict[str, list[str]]:
        return {"ran": list(background_log)}

    return app
