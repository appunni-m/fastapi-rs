"""Independent ASGI inputs for the pinned First Steps documentation sections."""

from fastapi import FastAPI


def create_app(factory_input: dict, _event_trace: list[str]) -> FastAPI:
    """Create a handler variant with a response distinct from the docs example."""
    app = FastAPI()
    handler_kind = factory_input["handler_kind"]

    if handler_kind == "async":

        @app.get("/")
        async def root():
            return {"greeting": "independent async sample"}

    elif handler_kind == "sync":

        @app.get("/")
        def root():
            return {"greeting": "independent sync sample"}

    else:
        raise ValueError("unsupported First Steps input variant")

    return app
