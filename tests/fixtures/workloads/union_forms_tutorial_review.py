"""Independent URL-encoded union-of-model form workload."""

from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel


class UserForm(BaseModel):
    name: str
    email: str


class CompanyForm(BaseModel):
    company_name: str
    industry: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/form-union/")
    def post_union_form(data: Annotated[UserForm | CompanyForm, Form()]):
        return {"received": data}

    return app
