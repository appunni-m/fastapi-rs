from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/atlas/test_path_params_test_tutorial004_test_root_file_path/files/{file_path:path}")
    async def read_file(file_path: str):
        return {"file_path": file_path}

    return app
