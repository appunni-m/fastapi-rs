"""Independent ASGI workload for background task keyword argument forwarding."""

from fastapi import BackgroundTasks, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    delivery_events: list[str] = []

    def record_delivery(target: str, *, label: str) -> None:
        delivery_events.append(f"{target}:{label}")

    @app.post("/queue-delivery/{target}")
    async def queue_delivery(target: str, background_tasks: BackgroundTasks) -> dict[str, str]:
        background_tasks.add_task(record_delivery, target, label="mirror-refresh")
        return {"queued": target}

    @app.get("/delivery-ledger")
    def read_delivery_ledger() -> dict[str, list[str]]:
        return {"events": list(delivery_events)}

    return app
