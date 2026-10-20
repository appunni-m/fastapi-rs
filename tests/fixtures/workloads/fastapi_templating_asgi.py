"""Exercise FastAPI's Jinja2Templates re-export in a rendered HTTP response."""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from jinja2 import DictLoader, Environment


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()
    environment = Environment(
        loader=DictLoader({"item.html": "<p>{{ request.url.path }}:{{ item_id }}</p>"})
    )
    templates = Jinja2Templates(env=environment)

    @app.get("/items/{item_id}")
    async def read_item(request: Request, item_id: str):
        return templates.TemplateResponse(
            request=request,
            name="item.html",
            context={"item_id": item_id},
        )

    return app
