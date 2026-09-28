"""Independent FastAPI source-oracle stimuli for the pending source wave."""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Response,
    Security,
    UploadFile,
)
from fastapi.responses import EventSourceResponse, JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel, ConfigDict


class DeliveryPoint(BaseModel):
    """The customer-facing delivery address.\fPrivate dispatch notes."""

    street: str
    district: str


class DeliveryManifest(BaseModel):
    reference: str
    destination: DeliveryPoint


class ApplicantInput(BaseModel):
    given_name: str
    family_name: str


class ApplicantRecord(ApplicantInput):
    model_config = ConfigDict(from_attributes=True)

    @property
    def label(self) -> str:
        return f"{self.given_name} {self.family_name}"


class ApplicantView(ApplicantInput):
    label: str
    model_config = ConfigDict(from_attributes=True)


class ApiFaultItem(BaseModel):
    category: str
    description: str


class ApiFaultCollection(BaseModel):
    errors: list[ApiFaultItem]


class PairBundle(BaseModel):
    pairs: list[tuple[str, str]]


class Point(BaseModel):
    x: float
    y: float


class ContentRecord(BaseModel):
    label: str
    amount: float


class TutorialRecord(BaseModel):
    heading: str
    quantity: int


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    """Build one small public app for the case's named behavior family."""
    scenario = factory_input.get("scenario")
    if scenario == "upload-close":
        return _upload_close_app()
    if scenario == "security-scopes":
        return _security_scopes_app()
    if scenario == "formfeed-schema":
        return _formfeed_schema_app()
    if scenario == "orm-response":
        return _orm_response_app()
    if scenario == "response-cookies":
        return _response_cookies_app()
    if scenario == "response-bodyless":
        return _response_bodyless_app()
    if scenario == "response-overwrite":
        return _response_overwrite_app()
    if scenario == "response-model-subtypes":
        return _response_model_subtypes_app()
    if scenario == "stream-status":
        return _stream_status_app()
    if scenario == "tuple-validation":
        return _tuple_validation_app()
    if scenario in {"content-app", "content-nested", "content-tutorial"}:
        return _content_type_app(str(scenario))
    raise ValueError(f"unknown pending source-wave scenario: {scenario!r}")


def _upload_close_app() -> FastAPI:
    app = FastAPI()
    observed_files: list[UploadFile] = []

    @app.post("/attachments")
    async def accept_attachment(file: UploadFile) -> dict[str, str | None]:
        observed_files.append(file)
        return {"filename": file.filename}

    return app


def _security_scopes_app() -> FastAPI:
    app = FastAPI()
    bearer = OAuth2PasswordBearer(tokenUrl="/session/token")

    def collect_access(
        credential: Annotated[str | None, Security(bearer)],
        scopes: SecurityScopes,
    ) -> dict[str, Any]:
        required = {"archive:read", "billing:write"}
        if not required.issubset(set(scopes.scopes)):
            raise HTTPException(status_code=401, detail="required access scopes are absent")
        return {"credential": credential, "scopes": scopes.scopes}

    @app.get("/security/credential")
    def credential_view(
        access: Annotated[
            dict[str, Any],
            Security(collect_access, scopes=["archive:read", "billing:write"]),
        ],
    ) -> dict[str, Any]:
        return access

    @app.get(
        "/security/with-scopes",
        dependencies=[Security(collect_access, scopes=["archive:read", "billing:write"])],
    )
    def scoped_control() -> dict[str, str]:
        return {"state": "scope accepted"}

    @app.get("/security/without-scopes", dependencies=[Security(collect_access)])
    def unscoped_control() -> dict[str, str]:
        return {"state": "scope absent"}

    return app


def _formfeed_schema_app() -> FastAPI:
    app = FastAPI()

    @app.get("/catalog/{reference}", response_model=DeliveryManifest)
    def read_manifest(reference: str) -> DeliveryManifest:
        return DeliveryManifest(
            reference=reference,
            destination=DeliveryPoint(street="18 Cedar Walk", district="Northbank"),
        )

    return app


def _orm_response_app() -> FastAPI:
    app = FastAPI()

    @app.post("/directory/", response_model=ApplicantView)
    def create_applicant(person: ApplicantInput) -> ApplicantRecord:
        return ApplicantRecord.model_validate(person)

    return app


def _response_cookies_app() -> FastAPI:
    app = FastAPI()

    def set_ticket(*, response: Response) -> dict[str, str]:
        response.set_cookie("session-ticket", "wave-a", httponly=True)
        return {"state": "issued"}

    def relay_ticket(*, item: Annotated[dict[str, str], Depends(set_ticket)]) -> dict[str, str]:
        return item

    @app.get("/ticket/direct")
    def direct_ticket(
        item: Annotated[dict[str, str], Depends(set_ticket)],
    ) -> dict[str, dict[str, str]]:
        return {"item": item}

    @app.get("/ticket/relayed")
    def relayed_ticket(
        item: Annotated[dict[str, str], Depends(relay_ticket)],
    ) -> dict[str, dict[str, str]]:
        return {"item": item}

    return app


def _response_bodyless_app() -> FastAPI:
    app = FastAPI()

    class ProblemJSONResponse(JSONResponse):
        media_type = "application/problem+json"

    @app.get(
        "/responses/nothing",
        status_code=204,
        response_class=ProblemJSONResponse,
        responses={503: {"description": "Catalog unavailable", "model": ApiFaultCollection}},
    )
    async def no_content() -> None:
        return None

    return app


def _response_overwrite_app() -> FastAPI:
    app = FastAPI()

    @app.delete("/inventory/{record_id}", status_code=204, response_model=None)
    async def archive_record(record_id: int, response: Response) -> dict[str, int | str]:
        response.status_code = 409
        return {"record": record_id, "state": "retained"}

    return app


def _response_model_subtypes_app() -> FastAPI:
    app = FastAPI()

    class ArchiveCard(BaseModel):
        title: str

    @app.get("/schemas/integer", responses={"503": {"model": int}})
    def integer_fault() -> None:
        return None

    @app.get("/schemas/integer-list", responses={"503": {"model": list[int]}})
    def integer_list_fault() -> None:
        return None

    @app.get("/schemas/card", responses={"503": {"model": ArchiveCard}})
    def card_fault() -> None:
        return None

    @app.get("/schemas/card-list", responses={"503": {"model": list[ArchiveCard]}})
    def card_list_fault() -> None:
        return None

    return app


def _stream_status_app() -> FastAPI:
    app = FastAPI()

    async def select_accepted(response: Response) -> None:
        response.status_code = 202

    @app.post("/streams/sse", response_class=EventSourceResponse, status_code=201)
    async def sse_declared() -> AsyncIterable[dict[str, str]]:
        yield {"record": "queued"}

    @app.post("/streams/jsonl", status_code=201)
    async def jsonl_declared() -> AsyncIterable[dict[str, str]]:
        yield {"record": "queued"}

    @app.post("/streams/raw", response_class=StreamingResponse, status_code=201)
    async def raw_declared() -> AsyncIterable[str]:
        yield "queued"

    @app.post(
        "/streams/sse-dependency",
        response_class=EventSourceResponse,
        responses={202: {"description": "Accepted event stream"}},
    )
    async def sse_dependency(_: None = Depends(select_accepted)) -> AsyncIterable[dict[str, str]]:
        yield {"record": "accepted"}

    @app.post(
        "/streams/jsonl-dependency",
        responses={202: {"description": "Accepted line stream"}},
    )
    async def jsonl_dependency(_: None = Depends(select_accepted)) -> AsyncIterable[dict[str, str]]:
        yield {"record": "accepted"}

    @app.post(
        "/streams/raw-dependency",
        response_class=StreamingResponse,
        responses={202: {"description": "Accepted raw stream"}},
    )
    async def raw_dependency(_: None = Depends(select_accepted)) -> AsyncIterable[str]:
        yield "accepted"

    @app.post(
        "/streams/sse-override",
        response_class=EventSourceResponse,
        status_code=201,
        responses={202: {"description": "Accepted event stream"}},
    )
    async def sse_override(_: None = Depends(select_accepted)) -> AsyncIterable[dict[str, str]]:
        yield {"record": "overridden"}

    @app.post(
        "/streams/jsonl-override",
        status_code=201,
        responses={202: {"description": "Accepted line stream"}},
    )
    async def jsonl_override(_: None = Depends(select_accepted)) -> AsyncIterable[dict[str, str]]:
        yield {"record": "overridden"}

    @app.post(
        "/streams/raw-override",
        response_class=StreamingResponse,
        status_code=201,
        responses={202: {"description": "Accepted raw stream"}},
    )
    async def raw_override(_: None = Depends(select_accepted)) -> AsyncIterable[str]:
        yield "overridden"

    return app


def _tuple_validation_app() -> FastAPI:
    app = FastAPI()

    @app.post("/tuples/pairs")
    def pair_bundle(payload: PairBundle) -> PairBundle:
        return payload

    @app.post("/tuples/points")
    def point_pair(points: tuple[Point, Point]) -> tuple[Point, Point]:
        return points

    @app.post("/tuples/form")
    def form_pair(values: tuple[int, int] = Form()) -> tuple[int, int]:
        return values

    return app


def _content_type_app(scenario: str) -> FastAPI:
    if scenario == "content-app":
        app = FastAPI()

        @app.post("/strict/items")
        async def strict_item(data: dict[str, Any]) -> dict[str, Any]:
            return data

        lax_app = FastAPI(strict_content_type=False)

        @lax_app.post("/items")
        async def lax_item(data: dict[str, Any]) -> dict[str, Any]:
            return data

        app.mount("/lax-app", lax_app)
        return app

    if scenario == "content-nested":
        root = FastAPI(strict_content_type=True)
        lax_app = FastAPI(strict_content_type=False)
        lax_outer = APIRouter(prefix="/outer")
        strict_inner = APIRouter(prefix="/strict", strict_content_type=True)
        default_inner = APIRouter(prefix="/default")

        @strict_inner.post("/items")
        async def nested_strict(data: dict[str, Any]) -> dict[str, Any]:
            return data

        @default_inner.post("/items")
        async def nested_default(data: dict[str, Any]) -> dict[str, Any]:
            return data

        lax_outer.include_router(strict_inner)
        lax_outer.include_router(default_inner)
        lax_app.include_router(lax_outer)
        root.mount("/nested-lax", lax_app)

        mixed_outer = APIRouter(prefix="/outer", strict_content_type=False)
        mixed_inner = APIRouter(prefix="/inner", strict_content_type=True)

        @mixed_outer.post("/items")
        async def mixed_lax(data: dict[str, Any]) -> dict[str, Any]:
            return data

        @mixed_inner.post("/items")
        async def mixed_strict(data: dict[str, Any]) -> dict[str, Any]:
            return data

        mixed_outer.include_router(mixed_inner)
        root.include_router(mixed_outer, prefix="/mixed")
        return root

    tutorial = FastAPI(strict_content_type=False)

    @tutorial.post("/guide/items")
    async def guide_item(data: TutorialRecord) -> TutorialRecord:
        return data

    return tutorial
