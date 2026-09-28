from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class CatalogueItem(BaseModel):
    item_id: int
    label: str


async def get_workspace(x_workspace: Annotated[str, Header(alias="X-Workspace")]) -> str:
    return x_workspace


async def record_task(queue: list[str], task_name: str) -> None:
    queue.append(task_name)


oauth2 = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={"reports:read": "Read report summaries"},
)


def create_app() -> FastAPI:
    task_queue: list[str] = []
    app = FastAPI()
    catalogue = APIRouter(prefix="/v2", tags=["catalogue"])

    @catalogue.get("/items/{item_id}", response_model=CatalogueItem)
    async def get_catalogue_item(item_id: int) -> CatalogueItem:
        return CatalogueItem(item_id=item_id, label=f"item-{item_id}")

    app.include_router(catalogue)

    @app.get("/workspace")
    async def read_workspace(
        workspace: Annotated[str, Depends(get_workspace)],
    ) -> dict[str, str]:
        return {"workspace": workspace}

    @app.get("/scoped-report")
    async def read_scoped_report(
        token: Annotated[str, Security(oauth2, scopes=["reports:read"])],
    ) -> dict[str, str]:
        return {"token": token, "report": "summary"}

    @app.get("/widgets/{widget_id}")
    async def read_widget(
        widget_id: Annotated[int, Path(gt=0)],
        scale: Annotated[float, Query(gt=0)],
        region: Annotated[str, Header(alias="X-Region", min_length=2)],
    ) -> dict[str, object]:
        return {"widget_id": widget_id, "scale": scale, "region": region}

    @app.post("/inspect")
    async def inspect_request(request: Request) -> dict[str, object]:
        body = await request.json()
        return {
            "method": request.method,
            "path": request.url.path,
            "mode": request.query_params.get("mode"),
            "payload": body,
        }

    @app.get("/response-envelope")
    async def make_response(response: Response) -> dict[str, str]:
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["x-response-source"] = "route-parameter"
        response.set_cookie(key="view", value="summary", httponly=True)
        return {"result": "queued"}

    @app.post("/scheduled/{task_name}")
    async def schedule_task(task_name: str, background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(record_task, task_queue, task_name)
        return {"scheduled": task_name}

    @app.get("/scheduled")
    async def list_scheduled() -> dict[str, list[str]]:
        return {"tasks": task_queue}

    return app
