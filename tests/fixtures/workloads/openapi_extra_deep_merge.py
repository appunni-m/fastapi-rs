from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/direct",
        summary="Generated direct summary",
        tags=["direct-base"],
        response_model=list[str],
        openapi_extra={
            "summary": "Extra direct summary",
            "tags": ["direct-extra"],
            "responses": {
                "200": {
                    "description": "Extra direct response",
                    "x-response-extension": {"owner": "direct"},
                }
            },
            "x-fastapi-rs-extra": {"nested": {"owner": "direct"}},
        },
    )
    async def direct_items() -> list[str]:
        return ["direct"]

    router = APIRouter()

    @router.get(
        "/router",
        summary="Generated router summary",
        tags=["router-base"],
        response_model=list[str],
        openapi_extra={
            "summary": "Extra router summary",
            "tags": ["router-extra"],
            "responses": {
                "200": {
                    "description": "Extra router response",
                    "x-response-extension": {"owner": "router"},
                }
            },
            "x-fastapi-rs-extra": {"nested": {"owner": "router"}},
        },
    )
    async def router_items() -> list[str]:
        return ["router"]

    app.include_router(router, prefix="/v1", tags=["included-router"])
    return app
