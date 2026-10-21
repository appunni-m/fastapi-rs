"""Independent workload for request-scoped BackgroundTasks injection."""

import asyncio
from functools import partial
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.responses import JSONResponse, Response
from starlette.background import BackgroundTask
from starlette.background import BackgroundTasks as StarletteBackgroundTasks


def create_app(factory_input: dict[str, object], _workload_trace: list[str]) -> FastAPI:
    del factory_input, _workload_trace
    app = FastAPI()
    task_events: list[str] = []
    default_background_tasks = BackgroundTasks()

    def record_task(label: str) -> None:
        task_events.append(label)

    async def record_async_task(label: str) -> None:
        task_events.append(label)

    def fail_task(label: str) -> None:
        task_events.append(label)
        raise ValueError("background-task-failure")

    async def append_live_task(tasks: list[BackgroundTask]) -> None:
        task_events.append("live-mutator")
        tasks.append(BackgroundTask(record_task, "live-appended"))

    def record_keyword_task(label: str, **values: str) -> None:
        encoded_values = ",".join(f"{key}={value}" for key, value in values.items())
        task_events.append(f"{label}:{encoded_values}")

    async def record_partial_task(label: str, *, detail: str) -> None:
        task_events.append(f"{label}:{detail}")

    class BoundTaskRecorder:
        def record(self, label: str, *, detail: str) -> None:
            task_events.append(f"{label}:{detail}")

    class AsyncTaskRecorder:
        async def __call__(self, label: str) -> None:
            task_events.append(label)

    def add_base_typed_task(background_tasks: StarletteBackgroundTasks) -> str:
        background_tasks.add_task(record_task, "starlette-base-dependency")
        return "base-annotated"

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

    @app.get("/mixed")
    async def mixed_sync_async_tasks(background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(record_task, "sync-first")
        background_tasks.add_task(record_async_task, "async-second")
        background_tasks.add_task(record_task, "sync-third")
        return {"kind": "mixed"}

    @app.get("/constructor")
    def constructor_task_sequence() -> Response:
        background = BackgroundTasks(
            [
                BackgroundTask(record_task, "constructor-sync-first"),
                BackgroundTask(record_async_task, "constructor-async-second"),
                BackgroundTask(record_task, "constructor-sync-third"),
            ]
        )
        return Response("constructed", media_type="text/plain", background=background)

    @app.get("/live-list")
    async def mutate_live_task_list(background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(append_live_task, background_tasks.tasks)
        background_tasks.add_task(record_task, "live-original-tail")
        return {"kind": "live-list"}

    @app.get("/failure")
    async def fail_during_task_sequence(background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(record_task, "failure-first")
        background_tasks.add_task(fail_task, "failure-raised")
        background_tasks.add_task(record_task, "failure-skipped")
        return {"kind": "failure"}

    @app.get("/cancel-background-task")
    async def schedule_cancellable_task(background_tasks: BackgroundTasks) -> dict[str, str]:
        async def wait_until_cancelled() -> None:
            task_events.append("started")
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                task_events.append("cancelled")
                raise

        background_tasks.add_task(wait_until_cancelled)
        return {"kind": "cancellation"}

    @app.get("/default-background-tasks")
    async def use_request_background_tasks_with_default(
        background_tasks: BackgroundTasks = default_background_tasks,
    ) -> dict[str, bool]:
        background_tasks.add_task(record_task, "request-scoped-default-parameter")
        return {"uses_default_instance": background_tasks is default_background_tasks}

    @app.get("/callable-shapes")
    async def execute_callable_shapes(background_tasks: BackgroundTasks) -> dict[str, str]:
        bound_recorder = BoundTaskRecorder()
        async_recorder = AsyncTaskRecorder()
        async_partial = partial(record_partial_task, "async-partial")
        nested_async_partial = partial(async_partial, detail="nested-keyword")
        background_tasks.add_task(bound_recorder.record, "bound-method", detail="bound-keyword")
        background_tasks.add_task(async_recorder, "async-callable-instance")
        background_tasks.add_task(partial(record_task, "sync-partial"))
        background_tasks.add_task(nested_async_partial)
        background_tasks.add_task(
            record_keyword_task, "keyword-order", second="second", first="first"
        )
        return {"kind": "callable-shapes"}

    @app.get("/starlette-base-annotation")
    async def inject_starlette_base_annotation(
        background_tasks: BackgroundTasks,
        dependency_value: Annotated[str, Depends(add_base_typed_task)],
    ) -> dict[str, str | bool]:
        background_tasks.add_task(record_task, "fastapi-endpoint")
        return {
            "dependency": dependency_value,
            "is_fastapi_background_tasks": isinstance(background_tasks, BackgroundTasks),
        }

    @app.get("/events")
    def read_task_events() -> dict[str, list[str]]:
        return {"events": list(task_events)}

    return app
