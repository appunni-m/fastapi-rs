"""Independent Response-reference inputs without cookie or response-model cases."""

from fastapi import FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/injected")
    async def injected_response(response: Response):
        response.status_code = 202
        response.headers["X-Response-Source"] = "injected-parameter"
        return {"state": "queued"}

    @app.get("/returned")
    async def returned_response():
        return Response(
            content="created",
            status_code=201,
            headers={"X-Response-Source": "returned-instance"},
            media_type="text/plain",
        )

    return app
