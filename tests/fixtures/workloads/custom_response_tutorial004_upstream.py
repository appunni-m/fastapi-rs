"""Independent workload for FastAPI 0.141.1 custom-response tutorial 004."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def create_app() -> FastAPI:
    app = FastAPI()

    def generate_html_response():
        html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
        return HTMLResponse(content=html_content, status_code=200)

    @app.get("/items/", response_class=HTMLResponse)
    async def read_items():
        return generate_html_response()

    return app
