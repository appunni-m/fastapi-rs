"""Independent input app for selected pending OpenAPI source cases."""

from enum import Enum

from fastapi import APIRouter, Body, Cookie, Depends, FastAPI, Header, Path, Query
from pydantic import BaseModel, ConfigDict, Field


class EventKind(str, Enum):
    created = "created"
    updated = "updated"


class NestedEvent(BaseModel):
    kind: EventKind = Field(default=EventKind.created)
    text: str


class MessageResult(BaseModel):
    text: str = ""
    events: list[NestedEvent] = Field(default_factory=list)


class MessageRecord(BaseModel):
    prompt: str
    result: MessageResult


class FormFeedModel(BaseModel):
    """First part of a model description.\fDocumentation after the break."""

    value: str


class ExampleItem(BaseModel):
    value: str

    model_config = ConfigDict(json_schema_extra={"example": {"value": "model-level-example"}})


_BODY_EXAMPLES = Body(examples=[{"value": "request-body-one"}, {"value": "request-body-two"}])


def create_app() -> FastAPI:
    app = FastAPI(title="Source Review Input", version="1.0")

    @app.post("/messages", response_model=MessageRecord)
    async def create_message(prompt: str) -> MessageRecord:
        return MessageRecord(
            prompt=prompt,
            result=MessageResult(text=f"Processed: {prompt}"),
        )

    @app.get("/description")
    def describe_model(record: FormFeedModel):
        return record

    def common_header(*, marker: str = Header()):
        return marker

    def nested_header(*, marker: str = Depends(common_header)):
        return f"{marker}:nested"

    @app.get("/shared-header")
    def read_shared_header(
        direct: str = Depends(common_header),
        nested: str = Depends(nested_header),
    ):
        return {"direct": direct, "nested": nested}

    left_router = APIRouter()
    right_router = APIRouter()

    @left_router.post("/compute")
    def compute_left(left: int = Body(), right: str = Body()):
        return {"left": left, "right": right}

    @right_router.post("/compute/")
    def compute_right(left: int = Body(), right: str = Body()):
        return {"left": left, "right": right}

    app.include_router(left_router, prefix="/left")
    app.include_router(right_router, prefix="/right")

    @app.post("/examples/model")
    def model_example(item: ExampleItem):
        return item

    @app.post("/examples/body")
    def body_examples(item: ExampleItem = _BODY_EXAMPLES):
        return item

    @app.get("/examples/path/{value}")
    def path_examples(
        value: str = Path(examples=["path-one", "path-two"]),
    ):
        return value

    @app.get("/examples/query")
    def query_examples(
        value: str | None = Query(default=None, examples=["query-one", "query-two"]),
    ):
        return value

    @app.get("/examples/header")
    def header_examples(
        value: str | None = Header(default=None, examples=["header-one", "header-two"]),
    ):
        return value

    @app.get("/examples/cookie")
    def cookie_examples(
        value: str | None = Cookie(default=None, examples=["cookie-one", "cookie-two"]),
    ):
        return value

    return app
