import yaml
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError


class AtlasEntry(BaseModel):
    name: str
    tags: list[str]


def create_app() -> FastAPI:
    app = FastAPI()
    schema = AtlasEntry.model_json_schema()

    @app.post(
        "/atlas/test_path_operation_advanced_configurations_test_tutorial007_test_post_broken_yaml/items/",
        openapi_extra={
            "requestBody": {"required": True, "content": {"application/x-yaml": {"schema": schema}}}
        },
    )
    async def parse_yaml(request: Request):
        raw = await request.body()
        try:
            value = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise HTTPException(status_code=422, detail="Malformed atlas YAML") from exc
        try:
            entry = AtlasEntry.model_validate(value)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
        return entry

    return app
