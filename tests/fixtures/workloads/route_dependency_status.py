"""Input-only workload for HTTP route-level dependencies and response state."""

from fastapi import Depends, FastAPI, Response


async def mark_queued(response: Response) -> None:
    response.status_code = 202


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/queue", dependencies=[Depends(mark_queued)])
    async def queue_status() -> dict[str, str]:
        return {"state": "queued"}

    return app
