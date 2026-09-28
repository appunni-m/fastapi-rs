from fastapi import FastAPI, Request


def magic_data_reader(raw_body: bytes) -> dict:
    return {
        "size": len(raw_body),
        "content": {
            "name": "Maaaagic",
            "price": 42,
            "description": "Just kiddin', no magic here. ✨",
        },
    }


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/items/",
        openapi_extra={
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "required": ["name", "price"],
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "price": {"type": "number"},
                                "description": {"type": "string"},
                            },
                        }
                    }
                },
                "required": True,
            }
        },
    )
    async def create_item(request: Request):
        return magic_data_reader(await request.body())

    return app
