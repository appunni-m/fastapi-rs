"""Independent inputs for router metadata and request-configuration parity."""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, Path, Query, Response
from fastapi.responses import JSONResponse


class WaveResponse0(JSONResponse):
    media_type = "application/x-wave-0"


class WaveResponse1(JSONResponse):
    media_type = "application/x-wave-1"


class WaveResponse2(JSONResponse):
    media_type = "application/x-wave-2"


class WaveResponse3(JSONResponse):
    media_type = "application/x-wave-3"


class WaveResponse4(JSONResponse):
    media_type = "application/x-wave-4"


class WaveResponse5(JSONResponse):
    media_type = "application/x-wave-5"


async def _mark_app(response: Response) -> None:
    response.headers["x-wave-app"] = "present"


async def _mark_include(response: Response) -> None:
    response.headers["x-wave-include"] = "present"


async def _mark_nested(response: Response) -> None:
    response.headers["x-wave-nested"] = "present"


async def _mark_route(response: Response) -> None:
    response.headers["x-wave-route"] = "present"


def create_app() -> FastAPI:
    app = FastAPI(
        dependencies=[Depends(_mark_app)],
        default_response_class=WaveResponse0,
        strict_content_type=True,
    )

    direct = APIRouter(dependencies=[Depends(_mark_include)])

    @direct.get("/explicit", response_class=WaveResponse1, dependencies=[Depends(_mark_route)])
    async def explicit_response_class(value: str):
        return value

    @direct.get("/inherited")
    async def inherited_response_class(value: str):
        return value

    app.include_router(direct, prefix="/response", default_response_class=WaveResponse1)

    leaf = APIRouter()

    @leaf.get("/explicit", response_class=WaveResponse3, dependencies=[Depends(_mark_route)])
    async def nested_explicit_response(value: str):
        return value

    @leaf.get("/inherited")
    async def nested_inherited_response(value: str):
        return value

    middle = APIRouter()
    middle.include_router(
        leaf,
        prefix="/leaf",
        dependencies=[Depends(_mark_nested)],
        default_response_class=WaveResponse2,
    )
    outer = APIRouter()
    outer.include_router(
        middle,
        prefix="/middle",
        dependencies=[Depends(_mark_include)],
        default_response_class=WaveResponse1,
    )
    app.include_router(outer, prefix="/depth-three")

    deepest = APIRouter()

    @deepest.get("/explicit", response_class=WaveResponse5, dependencies=[Depends(_mark_route)])
    async def five_level_explicit_response(value: str):
        return value

    @deepest.get("/inherited")
    async def five_level_inherited_response(value: str):
        return value

    level4 = APIRouter()
    level4.include_router(deepest, prefix="/level5", default_response_class=WaveResponse4)
    level3 = APIRouter()
    level3.include_router(level4, prefix="/level4", default_response_class=WaveResponse3)
    level2 = APIRouter()
    level2.include_router(level3, prefix="/level3", default_response_class=WaveResponse2)
    level1 = APIRouter()
    level1.include_router(level2, prefix="/level2", default_response_class=WaveResponse1)
    app.include_router(level1, prefix="/depth-five")

    metadata = APIRouter(tags=["wave-router"])

    @metadata.get(
        "/documented",
        responses={418: {"description": "A reviewed response overlay"}},
    )
    async def documented_route():
        return {"item": "independent"}

    app.include_router(
        metadata,
        prefix="/metadata",
        tags=["wave-include"],
        responses={429: {"description": "An include-level response overlay"}},
    )

    lax_router = APIRouter(prefix="/content/lax", strict_content_type=False)
    strict_router = APIRouter(prefix="/content/strict", strict_content_type=True)
    default_router = APIRouter(prefix="/content/default")

    @lax_router.post("/record")
    async def lax_record(data: dict):
        return data

    @strict_router.post("/record")
    async def strict_record(data: dict):
        return data

    @default_router.post("/record")
    async def default_record(data: dict):
        return data

    app.include_router(lax_router)
    app.include_router(strict_router)
    app.include_router(default_router)

    templated = APIRouter()

    @templated.get("/users/{user_id}")
    async def templated_user(segment: str, user_id: str):
        return {"segment": segment, "user_id": user_id}

    app.include_router(templated, prefix="/{segment}")

    @app.get("/convert/int/{value:int}")
    async def integer_value(value: int = Path()):
        return {"integer": value}

    @app.get("/convert/float/{value:float}")
    async def float_value(value: float = Path()):
        return {"float": value}

    @app.get("/convert/path/{value:path}")
    async def path_value(value: str = Path()):
        return {"path": value}

    @app.get("/convert/query/")
    async def query_value(value: str = Query()):
        return {"query": value}

    return app
