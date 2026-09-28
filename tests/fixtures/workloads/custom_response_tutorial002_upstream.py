"""Independent workload for FastAPI 0.141.1 custom-response tutorial 002."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/", response_class=HTMLResponse)
    async def read_items():
        return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """

    return app
