from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/atlas/test_path_params_test_tutorial003b_test_get_users/users")
    async def first_registration():
        return {"registration": "first"}

    @app.get("/atlas/test_path_params_test_tutorial003b_test_get_users/users")
    async def second_registration():
        return {"registration": "second"}

    return app
