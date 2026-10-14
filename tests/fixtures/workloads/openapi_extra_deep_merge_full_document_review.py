from fastapi import FastAPI
from pydantic import BaseModel


class Entry(BaseModel):
    code: str
    title: str


def create_app() -> FastAPI:
    app = FastAPI(title="Operation Extension Review", version="1.2.3")

    @app.post(
        "/entries",
        summary="Generated entry operation",
        tags=["generated"],
        response_model=Entry,
        openapi_extra={
            "summary": "Reviewed entry operation",
            "tags": ["reviewed"],
            "responses": {
                "200": {
                    "description": "Reviewed success response",
                    "content": {
                        "application/json": {
                            "schema": {"description": "Schema annotation added by the extension"}
                        },
                        "application/vnd.example.entry+json": {
                            "schema": {
                                "type": "object",
                                "properties": {"code": {"type": "string"}},
                            }
                        },
                    },
                    "x-review": {"metadata": {"owner": "api-team"}},
                },
                "409": {
                    "description": "Entry conflict",
                    "content": {
                        "application/problem+json": {
                            "schema": {
                                "type": "object",
                                "properties": {"detail": {"type": "string"}},
                            }
                        }
                    },
                },
            },
        },
    )
    async def write_entry() -> Entry:
        return Entry(code="alpha", title="draft")

    return app
