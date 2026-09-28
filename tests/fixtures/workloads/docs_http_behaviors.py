from collections.abc import AsyncIterable, Callable
from typing import Annotated

from fastapi import APIRoute, APIRouter, BackgroundTasks, Body, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel


class StreamRecord(BaseModel):
    label: str
    ordinal: int


class BodyAuditRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def audit_request(request: Request) -> Response:
            body_size = len(await request.body())
            response = await original_route_handler(request)
            response.headers["x-body-size"] = str(body_size)
            return response

        return audit_request


async def record_job(jobs: list[str], job_id: str) -> None:
    jobs.append(job_id)


def create_app() -> FastAPI:
    jobs: list[str] = []
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://console.example"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["x-client-tag"],
        expose_headers=["x-body-size"],
    )

    @app.get("/resource")
    async def read_resource() -> dict[str, str]:
        return {"resource": "available"}

    @app.post("/jobs/{job_id}")
    async def enqueue_job(job_id: str, background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(record_job, jobs, job_id)
        return {"queued": job_id}

    @app.get("/jobs/state")
    async def job_state() -> dict[str, list[str]]:
        return {"jobs": jobs}

    @app.get("/events/feed", response_class=EventSourceResponse)
    async def stream_events() -> AsyncIterable[StreamRecord]:
        yield StreamRecord(label="first", ordinal=1)
        yield StreamRecord(label="second", ordinal=2)

    @app.get("/records/stream")
    async def stream_records() -> AsyncIterable[StreamRecord]:
        yield StreamRecord(label="oak", ordinal=1)
        yield StreamRecord(label="elm", ordinal=2)

    audit_router = APIRouter(route_class=BodyAuditRoute)

    @audit_router.post("/audit")
    async def audit_payload(
        payload: Annotated[dict[str, list[int]], Body()],
        request: Request,
    ) -> dict[str, int]:
        return {"total": sum(payload["values"]), "body_size": len(await request.body())}

    app.include_router(audit_router)
    return app
