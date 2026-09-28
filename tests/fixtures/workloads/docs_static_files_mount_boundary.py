"""Input workload for FastAPI mount and parent OpenAPI/docs isolation."""

from fastapi import FastAPI


async def mounted_asgi_child(scope, receive, send) -> None:
    """A minimal mounted ASGI app; this workflow does not request its paths."""
    if scope["type"] != "http":
        return
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain; charset=utf-8")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"mounted child",
            "more_body": False,
        }
    )


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", mounted_asgi_child, name="static")
    return app
