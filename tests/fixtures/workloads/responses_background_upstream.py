"""Independent ASGI stimuli for response construction and background work."""

from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


def create_app() -> FastAPI:
    app = FastAPI()
    completed_background_work: list[str] = []

    @app.get("/items/", response_class=HTMLResponse)
    async def read_html_items():
        return "<html><body><h1>Response</h1></body></html>"

    @app.get("/fastapi", response_class=RedirectResponse)
    async def redirect_fastapi():
        return "/destination"

    @app.get("/pydantic", response_class=RedirectResponse, status_code=302)
    async def redirect_pydantic():
        return "/destination"

    @app.get("/legacy/")
    def get_legacy_data():
        return Response(content="<legacy>ready</legacy>", media_type="application/xml")

    @app.get("/headers-and-object/")
    def get_headers(response: Response):
        response.headers["X-Probe"] = "present"
        return {"message": "headers"}

    @app.post("/cookie-and-object/")
    def create_cookie(response: Response):
        response.set_cookie(key="session", value="sample-session")
        return {"message": "cookie"}

    @app.post("/items/", status_code=201)
    async def create_item(name: str):
        return {"name": name}

    def record_notification(email: str):
        completed_background_work.append(f"notification:{email}")

    def record_message(email: str, query: str):
        completed_background_work.append(f"message:{email}:{query}")

    @app.post("/send-notification/{email}")
    async def send_notification(email: str, background_tasks: BackgroundTasks):
        background_tasks.add_task(record_notification, email)
        return {"message": "Notification scheduled"}

    @app.post("/send-message/{email}")
    async def send_message(email: str, q: str, background_tasks: BackgroundTasks):
        background_tasks.add_task(record_message, email, q)
        return {"message": "Message scheduled"}

    @app.get("/background-effects")
    def background_effects():
        return {"effects": completed_background_work}

    @app.get("/destination")
    def destination():
        return JSONResponse({"destination": True})

    return app
