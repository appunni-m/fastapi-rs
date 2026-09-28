"""Independent ASGI stimuli for cookies set through direct and nested dependencies."""

from typing import Annotated

from fastapi import Depends, FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()

    def set_cookie(*, response: Response) -> dict[str, str]:
        response.set_cookie("cookie-name", "cookie-value")
        return {}

    def set_indirect_cookie(dep: Annotated[dict[str, str], Depends(set_cookie)]):
        return dep

    @app.get("/directCookie")
    def get_direct_cookie(dep: Annotated[dict[str, str], Depends(set_cookie)]):
        return {"dep": dep}

    @app.get("/indirectCookie")
    def get_indirect_cookie(dep: Annotated[dict[str, str], Depends(set_indirect_cookie)]):
        return {"dep": dep}

    return app
