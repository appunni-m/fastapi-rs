"""Independent FastAPI webhook registration workload."""

from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from pydantic import BaseModel


class EventPayload(BaseModel):
    account: str
    amount: float
    occurred_at: datetime


def create_app() -> FastAPI:
    app = FastAPI()
    bearer = HTTPBearer()

    @app.webhooks.post("account-event")
    def account_event(
        payload: EventPayload,
        token: Annotated[str, Security(bearer)],
    ) -> None:
        del payload, token

    return app
