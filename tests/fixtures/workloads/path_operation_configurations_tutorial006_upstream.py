from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items():
        return [{"name": "Foo", "price": 42}]

    @app.get("/users/")
    async def read_users():
        return [{"username": "johndoe"}]

    @app.get("/elements/", deprecated=True)
    async def read_elements():
        return [{"item_id": "Foo"}]

    return app
