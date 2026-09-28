from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI()
    body_schema = {
        "type": "object",
        "required": ["reference"],
        "properties": {"reference": {"type": "string"}},
    }

    @app.post(
        "/atlas/test_path_operation_advanced_configurations_test_tutorial006_test_openapi_schema/items/",
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {"application/vnd.atlas-blob": {"schema": body_schema}},
            }
        },
    )
    async def read_raw(request: Request):
        raw = await request.body()
        return {"octets": len(raw), "token": raw.decode("utf-8")}

    return app
