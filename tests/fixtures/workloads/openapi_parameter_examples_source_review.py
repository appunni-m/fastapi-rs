"""Independent inputs for OpenAPI examples on HTTP parameter locations."""

from __future__ import annotations

from fastapi import Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel


class ParameterExampleRecord(BaseModel):
    data: str


_BODY_INFO = Body(
    examples=[{"data": "schema-body-value"}],
    openapi_examples={
        "body-entry": {
            "summary": "Body entry",
            "description": "Request-level body example",
            "value": {"data": "request-body-value"},
        },
        "alternate-body-entry": {
            "value": {"data": "alternate-request-body-value"},
        },
    },
)
_PATH_INFO = Path(
    examples=["schema-path-value"],
    openapi_examples={
        "path-entry": {
            "summary": "Path entry",
            "description": "Path parameter example",
            "value": "path-value",
        },
        "alternate-path-entry": {
            "value": "alternate-path-value",
        },
    },
)
_QUERY_INFO = Query(
    default=None,
    examples=["schema-query-value"],
    openapi_examples={
        "query-entry": {
            "summary": "Query entry",
            "description": "Query parameter example",
            "value": "query-value",
        },
        "alternate-query-entry": {
            "value": "alternate-query-value",
        },
    },
)
_HEADER_INFO = Header(
    default=None,
    examples=["schema-header-value"],
    openapi_examples={
        "header-entry": {
            "summary": "Header entry",
            "description": "Header parameter example",
            "value": "header-value",
        },
        "alternate-header-entry": {
            "value": "alternate-header-value",
        },
    },
)
_COOKIE_INFO = Cookie(
    default=None,
    examples=["schema-cookie-value"],
    openapi_examples={
        "cookie-entry": {
            "summary": "Cookie entry",
            "description": "Cookie parameter example",
            "value": "cookie-value",
        },
        "alternate-cookie-entry": {
            "value": "alternate-cookie-value",
        },
    },
)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/probe/body")
    def body_example(record: ParameterExampleRecord = _BODY_INFO) -> ParameterExampleRecord:
        return record

    @app.get("/probe/path/{sample_id}")
    def path_example(sample_id: str = _PATH_INFO) -> str:
        return sample_id

    @app.get("/probe/query")
    def query_example(sample: str | None = _QUERY_INFO) -> str | None:
        return sample

    @app.get("/probe/header")
    def header_example(sample: str | None = _HEADER_INFO) -> str | None:
        return sample

    @app.get("/probe/cookie")
    def cookie_example(sample: str | None = _COOKIE_INFO) -> str | None:
        return sample

    return app
