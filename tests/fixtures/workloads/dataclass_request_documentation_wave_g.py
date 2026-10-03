"""Independent ASGI input for stdlib dataclass request handling."""

from dataclasses import dataclass

from fastapi import FastAPI


@dataclass
class Entry:
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/entries/")
    async def create_entry(entry: Entry):
        return entry

    return app
