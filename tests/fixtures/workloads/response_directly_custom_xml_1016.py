"""Independent ASGI workload for directly returned custom XML responses."""

from fastapi import FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/feeds/{feed_id}")
    def read_feed(feed_id: str):
        body = f"<feed><id>{feed_id}</id><state>ready</state></feed>"
        return Response(content=body, media_type="application/xml")

    return app
