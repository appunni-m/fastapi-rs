from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/atlas/test_path_params_test_tutorial003_test_openapi_schema/users/me")
    async def read_reserved():
        return {"user_id": "reserved account"}

    @app.get("/atlas/test_path_params_test_tutorial003_test_openapi_schema/users/{user_id}")
    async def read_user(user_id: str):
        return {"user_id": user_id}

    return app
