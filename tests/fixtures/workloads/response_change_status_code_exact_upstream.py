"""Reproduce the pinned nested dependency status-code response workflow."""

from fastapi import Depends, FastAPI, Response


def create_app(factory_input, event_trace):
    """Build the exact route shape and payload used by the pinned source case."""
    del factory_input, event_trace
    app = FastAPI()

    async def response_status_setter(response: Response):
        response.status_code = 201

    async def parent_dep(result=Depends(response_status_setter)):  # noqa: B008
        return result

    @app.get("/", dependencies=[Depends(parent_dep)])
    async def get_main():
        return {"msg": "Hello World"}

    return app
