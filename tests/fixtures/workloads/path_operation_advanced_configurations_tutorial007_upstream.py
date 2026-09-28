import yaml
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError


class Item(BaseModel):
    name: str
    tags: list[str]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/items/",
        openapi_extra={
            "requestBody": {
                "content": {"application/x-yaml": {"schema": Item.model_json_schema()}},
                "required": True,
            }
        },
    )
    async def create_item(request: Request):
        raw_body = await request.body()
        try:
            data = yaml.safe_load(raw_body)
        except yaml.YAMLError as error:
            raise HTTPException(status_code=422, detail="Invalid YAML") from error
        try:
            item = Item.model_validate(data)
        except ValidationError as error:
            raise HTTPException(
                status_code=422,
                detail=error.errors(include_url=False),
            ) from error
        return item

    return app
