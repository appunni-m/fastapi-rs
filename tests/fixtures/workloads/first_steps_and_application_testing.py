"""Independent ASGI inputs for basic routes, OpenAPI, and lifespan-backed data."""

from contextlib import asynccontextmanager

from fastapi import FastAPI


def create_app(factory_input: dict, event_trace: list[str]) -> FastAPI:
    """Build one of the small applications represented by a recipe case."""
    app = FastAPI()
    app_kind = factory_input["app_kind"]

    if app_kind == "first_steps_async":

        @app.get("/")
        async def root():
            return {"message": "Hello World"}

    elif app_kind == "first_steps_sync":

        @app.get("/")
        def root():
            return {"message": "Hello World"}

    elif app_kind == "first_steps_async_independent":

        @app.get("/welcome")
        async def independent_welcome():
            return {"message": "Welcome to the independent sample"}

    elif app_kind == "first_steps_sync_independent":

        @app.get("/portal")
        def independent_portal():
            return {"message": "Independent synchronous sample"}

    elif app_kind == "application_testing":

        @app.get("/")
        async def read_main():
            return {"msg": "Hello World"}

    elif app_kind == "application_testing_lifespan":
        items: dict[str, dict[str, str]] = {}

        @asynccontextmanager
        async def lifespan(_app: FastAPI):
            event_trace.append("startup")
            items.update({"foo": {"name": "Fighters"}, "bar": {"name": "Tenders"}})
            try:
                yield
            finally:
                items.clear()
                event_trace.append("shutdown")

        app = FastAPI(lifespan=lifespan)

        @app.get("/items/{item_id}")
        async def read_items(item_id: str):
            return items[item_id]

    else:
        raise ValueError("unsupported authored application input")

    return app
