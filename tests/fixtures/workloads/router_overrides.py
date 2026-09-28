"""Independent nested-router defaults and response-override workload."""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, Response
from fastapi.responses import JSONResponse


class ResponseLevel0(JSONResponse):
    media_type = "application/x-level-0"


class ResponseLevel1(JSONResponse):
    media_type = "application/x-level-1"


class ResponseLevel2(JSONResponse):
    media_type = "application/x-level-2"


class ResponseLevel3(JSONResponse):
    media_type = "application/x-level-3"


class ResponseLevel4(JSONResponse):
    media_type = "application/x-level-4"


class ResponseLevel5(JSONResponse):
    media_type = "application/x-level-5"


async def dep0(response: Response) -> None:
    response.headers["x-level0"] = "True"


async def dep1(response: Response) -> None:
    response.headers["x-level1"] = "True"


async def dep2(response: Response) -> None:
    response.headers["x-level2"] = "True"


async def dep3(response: Response) -> None:
    response.headers["x-level3"] = "True"


async def dep4(response: Response) -> None:
    response.headers["x-level4"] = "True"


async def dep5(response: Response) -> None:
    response.headers["x-level5"] = "True"


router4_override = APIRouter(
    prefix="/level4",
    dependencies=[Depends(dep4)],
    default_response_class=ResponseLevel4,
)
router4_default = APIRouter()


@router4_override.get("/default5")
async def default5_from_level4(level5: str) -> str:
    return level5


@router4_override.get(
    "/override5",
    dependencies=[Depends(dep5)],
    response_class=ResponseLevel5,
)
async def override5_from_level4(level5: str) -> str:
    return level5


@router4_default.get("/default5")
async def default5_from_include(level5: str) -> str:
    return level5


@router4_default.get(
    "/override5",
    dependencies=[Depends(dep5)],
    response_class=ResponseLevel5,
)
async def override5_from_include(level5: str) -> str:
    return level5


router2_override = APIRouter(
    prefix="/level2",
    dependencies=[Depends(dep2)],
    default_response_class=ResponseLevel2,
)
router2_default = APIRouter()

for child_router in (router4_override, router4_default):
    router2_override.include_router(
        child_router,
        prefix="/level3",
        dependencies=[Depends(dep3)],
        default_response_class=ResponseLevel3,
    )
    router2_override.include_router(child_router)
    router2_default.include_router(
        child_router,
        prefix="/level3",
        dependencies=[Depends(dep3)],
        default_response_class=ResponseLevel3,
    )
    router2_default.include_router(child_router)


def create_app() -> FastAPI:
    app = FastAPI(
        dependencies=[Depends(dep0)],
        default_response_class=ResponseLevel0,
    )
    app.include_router(
        router2_override,
        prefix="/level1",
        dependencies=[Depends(dep1)],
        default_response_class=ResponseLevel1,
    )
    app.include_router(
        router2_default,
        prefix="/level1",
        dependencies=[Depends(dep1)],
        default_response_class=ResponseLevel1,
    )
    app.include_router(router2_override)
    app.include_router(router2_default)
    return app
