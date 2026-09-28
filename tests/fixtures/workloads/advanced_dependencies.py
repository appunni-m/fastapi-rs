"""Input workload for FastAPI's parameterized callable dependency example."""

from typing import Annotated

from fastapi import Depends, FastAPI


class FixedContentQueryChecker:
    def __init__(self, fixed_content: str) -> None:
        self.fixed_content = fixed_content

    def __call__(self, q: str = "") -> bool:
        return bool(q and self.fixed_content in q)


def create_app() -> FastAPI:
    app = FastAPI()
    checker = FixedContentQueryChecker("bar")

    @app.get("/query-checker/")
    async def read_query_check(
        fixed_content_included: Annotated[bool, Depends(checker)],
    ) -> dict[str, bool]:
        return {"fixed_content_in_query": fixed_content_included}

    return app
