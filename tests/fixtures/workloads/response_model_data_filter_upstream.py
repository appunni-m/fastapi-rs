"""Independent inputs for response-model subclass field filtering.

Behavior is sourced from the pinned FastAPI tests at
``tests/test_response_model_data_filter.py:8-17, 30-32, 35-53, 59-79``.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class AccountView(BaseModel):
    email: str


class AccountRegistration(AccountView):
    password: str


class StoredAccount(AccountView):
    password_hash: str


class CompanionRecord(BaseModel):
    name: str
    caretaker: StoredAccount


class CompanionView(BaseModel):
    name: str
    caretaker: AccountView


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/accounts/", response_model=AccountView)
    async def register_account(account: AccountRegistration) -> AccountRegistration:
        return account

    @app.get("/companions/{companion_id}", response_model=CompanionView)
    async def read_companion(companion_id: int) -> CompanionRecord:
        caretaker = StoredAccount(
            email="johndoe@example.com",
            password_hash="opaque-digest",
        )
        return CompanionRecord(name="Nibbler", caretaker=caretaker)

    @app.get("/companions/", response_model=list[CompanionView])
    async def read_companions() -> list[CompanionRecord]:
        caretaker = StoredAccount(
            email="johndoe@example.com",
            password_hash="opaque-digest",
        )
        return [
            CompanionRecord(name="Nibbler", caretaker=caretaker),
            CompanionRecord(name="Zoidberg", caretaker=caretaker),
        ]

    return app
