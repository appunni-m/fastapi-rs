"""Independent request-body workload for a model with a computed response field."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class QuoteInput(BaseModel):
    title: str
    amount: float
    surcharge: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/quotes")
    async def create_quote(quote: QuoteInput) -> dict[str, str | float | None]:
        result = quote.model_dump()
        if quote.surcharge is not None:
            result["total"] = quote.amount + quote.surcharge
        return result

    return app
