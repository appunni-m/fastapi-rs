"""Independent input for Response injection through a default Depends value."""

from fastapi import Depends, FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()

    def mark_response(response: Response) -> Response:
        response.headers["x-dependency-style"] = "default-value"
        return response

    @app.get("/response/dependency-default")
    def response_dependency_default(
        response: Response = Depends(mark_response),  # noqa: B008 - mirrors the public syntax under review
    ) -> dict[str, str]:
        return {"result": "default-parameter"}

    return app
