from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial006_test_openapi_schema/items/",
        tags=["assets"],
    )
    async def read_assets():
        return [{"title": "cedar"}]

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial006_test_openapi_schema/users/",
        tags=["operators"],
    )
    async def read_operators():
        return [{"handle": "mira"}]

    @app.get(
        "/atlas/test_path_operation_configurations_test_tutorial006_test_openapi_schema/elements/",
        tags=["assets"],
        deprecated=True,
    )
    async def read_legacy_assets():
        return [{"element": "flint"}]

    return app
