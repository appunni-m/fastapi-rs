"""Independent inputs for sync endpoints with async and sync yield dependencies."""

from collections.abc import AsyncIterator, Iterator

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    events: list[str] = []

    async def async_lease() -> AsyncIterator[str]:
        events.append("async-acquire")
        try:
            yield "copper-token"
        finally:
            events.append("async-release")

    def sync_lease() -> Iterator[str]:
        events.append("sync-acquire")
        try:
            yield "birch-token"
        finally:
            events.append("sync-release")

    @app.get("/leases/async")
    def use_async_lease(token: str = Depends(async_lease)) -> dict[str, object]:
        return {"token": token, "events": list(events)}

    @app.get("/leases/sync")
    def use_sync_lease(token: str = Depends(sync_lease)) -> dict[str, object]:
        return {"token": token, "events": list(events)}

    @app.get("/lease-events")
    def inspect_lease_events() -> dict[str, list[str]]:
        return {"events": list(events)}

    return app
