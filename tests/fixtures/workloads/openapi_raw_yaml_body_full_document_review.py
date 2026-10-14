from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI(title="Raw YAML Request", version="1.2.3")
    document_schema = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "labels": {"type": "array", "items": {"type": "string"}},
        },
    }

    @app.post(
        "/documents",
        openapi_extra={
            "requestBody": {
                "description": "The request is consumed as raw YAML bytes.",
                "required": True,
                "content": {"application/x-yaml": {"schema": document_schema}},
            }
        },
    )
    async def accept_document(request: Request) -> dict[str, int]:
        raw_payload = await request.body()
        return {"received_bytes": len(raw_payload)}

    return app
