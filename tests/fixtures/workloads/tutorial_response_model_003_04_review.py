"""Independent route construction input for an unsupported return annotation."""

from fastapi import FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/portal")
    async def get_portal(teleport: bool = False) -> Response | dict:
        if teleport:
            return Response(content="portal")
        return {"message": "independent portal input"}

    return app
