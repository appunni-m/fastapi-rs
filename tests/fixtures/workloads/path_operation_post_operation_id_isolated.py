from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items", operation_id="receiveItems")
    async def receive_items() -> dict[str, bool]:
        return {"accepted": True}

    return app
