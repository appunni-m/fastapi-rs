"""Exercise the FastAPI Response re-export as a direct ASGI application."""

from fastapi.responses import Response


def create_app() -> Response:
    return Response(
        content="direct résumé",
        status_code=207,
        headers={"X-Response-Contract": "direct"},
        media_type="text/plain",
    )
