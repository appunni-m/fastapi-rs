"""Path converter workload for nested and rooted file paths."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/files/{file_path:path}")
    async def read_file(file_path: str):
        return {"file_path": file_path}

    return app
