"""Input-only workload for Pydantic models in additional OpenAPI responses."""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class TeaError(BaseModel):
    message: str


class ApplicationUnauthorized(BaseModel):
    message: str


class ApplicationTeapot(BaseModel):
    message: str


class RouterPaymentRequired(BaseModel):
    message: str


class RouterConflict(BaseModel):
    message: str


class RouterLocked(BaseModel):
    message: str


class IncludedForbidden(BaseModel):
    message: str


class IncludedTeapot(BaseModel):
    message: str


class IncludedConflict(BaseModel):
    message: str


class OperationNotFound(BaseModel):
    message: str


class OperationLocked(BaseModel):
    message: str


def create_app() -> FastAPI:
    app = FastAPI(
        responses={
            401: {
                "description": "Application-level response",
                "model": ApplicationUnauthorized,
            },
            418: {
                "description": "Application response overridden by include",
                "model": ApplicationTeapot,
            },
        }
    )

    @app.get(
        "/tea",
        responses={418: {"description": "Teapot response", "model": TeaError}},
    )
    async def tea() -> dict[str, str]:
        return {"state": "ready"}

    router = APIRouter(
        responses={
            402: {
                "description": "Router-level response",
                "model": RouterPaymentRequired,
            },
            419: {
                "description": "Router response overrides include",
                "model": RouterConflict,
            },
            420: {
                "description": "Router response overridden by operation",
                "model": RouterLocked,
            },
        }
    )

    @router.get(
        "/items",
        responses={
            404: {
                "description": "Operation-level response",
                "model": OperationNotFound,
            },
            420: {
                "description": "Operation response overrides router",
                "model": OperationLocked,
            },
        },
    )
    async def items():
        return {"state": "ready"}

    app.include_router(
        router,
        prefix="/v1",
        responses={
            403: {
                "description": "Include-level response",
                "model": IncludedForbidden,
            },
            418: {
                "description": "Include response overrides application",
                "model": IncludedTeapot,
            },
            419: {
                "description": "Include response overridden by router",
                "model": IncludedConflict,
            },
        },
    )

    return app
