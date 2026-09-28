"""Input workload for an independently mounted FastAPI sub-application."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    subapi = FastAPI(title="Mounted API")

    @app.get("/app")
    async def read_main() -> dict[str, str]:
        return {"message": "Hello World from main app"}

    @subapi.get("/sub")
    async def read_sub() -> dict[str, str]:
        return {"message": "Hello World from sub API"}

    app.mount("/subapi", subapi)
    return app
