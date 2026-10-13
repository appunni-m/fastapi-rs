"""Input workload for operation IDs shared by paths and webhooks."""

from fastapi import FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/regular-event", operation_id="shared-event-operation")
    def regular_event():
        return {"accepted": True}

    @app.webhooks.post("event-notify", operation_id="shared-event-operation")
    def webhook_event():
        return {"accepted": True}

    return app
