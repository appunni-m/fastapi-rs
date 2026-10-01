"""Independent workload for request-scoped BackgroundTasks injection."""

from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI()
    task_events: list[str] = []

    def record_task(label: str) -> None:
        task_events.append(label)

    def add_nested_task(background_tasks: BackgroundTasks) -> str:
        background_tasks.add_task(record_task, "nested-dependency")
        return "nested"

    def add_parent_task(
        background_tasks: BackgroundTasks,
        nested: Annotated[str, Depends(add_nested_task)],
    ) -> str:
        background_tasks.add_task(record_task, "parent-dependency")
        return nested

    @app.get("/normal")
    async def normal_response(
        background_tasks: BackgroundTasks,
        dependency_value: Annotated[str, Depends(add_parent_task)],
    ) -> dict[str, str]:
        background_tasks.add_task(record_task, "normal-endpoint")
        return {"kind": "normal", "dependency": dependency_value}

    @app.get("/explicit")
    async def explicit_background_response(
        background_tasks: BackgroundTasks,
        dependency_value: Annotated[str, Depends(add_parent_task)],
    ) -> JSONResponse:
        background_tasks.add_task(record_task, "injected-endpoint")
        explicit_background = BackgroundTasks()
        explicit_background.add_task(record_task, "explicit-response")
        return JSONResponse(
            {"kind": "explicit", "dependency": dependency_value},
            background=explicit_background,
        )

    @app.get("/events")
    def read_task_events() -> dict[str, list[str]]:
        return {"events": list(task_events)}

    return app
