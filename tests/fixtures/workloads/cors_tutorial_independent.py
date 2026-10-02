from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://console.example.test", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["GET", "PATCH"],
        allow_headers=["Content-Type", "X-Workspace-Key"],
    )

    @app.get("/records/{record_id}")
    async def read_record(record_id: int) -> dict[str, int | str]:
        return {"record_id": record_id, "state": "ready"}

    @app.patch("/records/{record_id}")
    async def update_record(record_id: int) -> dict[str, int | str]:
        return {"record_id": record_id, "state": "updated"}

    return app
