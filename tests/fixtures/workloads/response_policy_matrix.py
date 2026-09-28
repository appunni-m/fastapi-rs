"""Independent response policy and serialization workload."""

from dataclasses import dataclass
from datetime import date

from fastapi import APIRouter, Depends, FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field


class GeneratedReceipt(BaseModel):
    code: int = 200
    message: str = Field(default_factory=lambda: "generated")


class ApiFault(BaseModel):
    reason: str


class Payload(BaseModel):
    title: str
    count: float | None = None


@dataclass
class CalendarEntry:
    title: str
    day: date
    count: float | None = None


def create_app() -> FastAPI:
    app = FastAPI(default_response_class=JSONResponse)

    async def set_created_status(response: Response) -> None:
        response.status_code = 201

    @app.get("/status-from-dependency", dependencies=[Depends(set_created_status)])
    async def status_from_dependency() -> dict[str, str]:
        return {"state": "created"}

    @app.delete("/records/{record_id}", status_code=204, response_model=None)
    async def delete_record(record_id: int, response: Response) -> dict[str, int | str]:
        response.status_code = 400
        return {"record": record_id, "state": "retained"}

    @app.get("/empty", status_code=204)
    async def empty_response() -> None:
        return None

    @app.get("/class/json")
    async def json_default() -> dict[str, str]:
        return {"format": "json"}

    @app.get("/class/plain", response_class=PlainTextResponse)
    async def plain_override() -> str:
        return "plain response"

    nested = APIRouter(default_response_class=PlainTextResponse)

    @nested.get("/plain")
    async def nested_plain_default() -> str:
        return "nested plain response"

    @nested.get("/html", response_class=HTMLResponse)
    async def nested_html_override() -> str:
        return "<p>nested html response</p>"

    app.include_router(nested, prefix="/nested")

    @app.get("/factory/dict", response_model=GeneratedReceipt)
    async def generated_receipt_dict() -> dict[str, int]:
        return {"code": 200}

    @app.get("/factory/model", response_model=GeneratedReceipt)
    async def generated_receipt_model() -> GeneratedReceipt:
        return GeneratedReceipt()

    @app.get("/payload/coerce", response_model=Payload)
    async def payload_coerce() -> dict[str, str | float]:
        return {"title": "coercion", "count": "2.5"}

    @app.get("/calendar/record", response_model=CalendarEntry)
    async def calendar_record() -> dict[str, str | float]:
        return {"title": "meeting", "day": "2025-04-12", "count": 2}

    @app.get("/calendar/object", response_model=CalendarEntry)
    async def calendar_object() -> CalendarEntry:
        return CalendarEntry(title="review", day=date(2025, 4, 12), count=3)

    @app.get(
        "/opaque",
        response_class=Response,
        responses={500: {"description": "Typed error", "model": ApiFault}},
    )
    async def opaque_response() -> Response:
        return Response(content=b"opaque")

    @app.get(
        "/array-errors",
        responses={500: {"description": "Typed errors", "model": list[ApiFault]}},
    )
    async def array_errors() -> dict[str, str]:
        return {"state": "ready"}

    return app
