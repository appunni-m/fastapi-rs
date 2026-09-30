"""Independent query-contract workload for FastAPI 0.141.1 docs examples."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import AfterValidator


def _check_id(value: str) -> str:
    if not value.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return value


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-example/t001/direct")
    async def tutorial001(q: str | None = None):
        return {"q": q}

    @app.get("/query-example/t002/direct")
    async def tutorial002_direct(q: str | None = Query(default=None, max_length=50)):
        return {"q": q}

    @app.get("/query-example/t002/annotated")
    async def tutorial002_annotated(
        q: Annotated[str | None, Query(max_length=50)] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t003/direct")
    async def tutorial003_direct(
        q: str | None = Query(default=None, min_length=3, max_length=50),
    ):
        return {"q": q}

    @app.get("/query-example/t003/annotated")
    async def tutorial003_annotated(
        q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t005/direct")
    async def tutorial005_direct(q: str = Query(default="oak", min_length=3)):
        return {"q": q}

    @app.get("/query-example/t005/annotated")
    async def tutorial005_annotated(
        q: Annotated[str, Query(min_length=3)] = "oak",
    ):
        return {"q": q}

    @app.get("/query-example/t006/direct")
    async def tutorial006_direct(q: str = Query(min_length=3)):
        return {"q": q}

    @app.get("/query-example/t006/annotated")
    async def tutorial006_annotated(q: Annotated[str, Query(min_length=3)]):
        return {"q": q}

    @app.get("/query-example/t006c/direct")
    async def tutorial006c_direct(q: str | None = Query(min_length=3)):
        return {"q": q}

    @app.get("/query-example/t006c/annotated")
    async def tutorial006c_annotated(
        q: Annotated[str | None, Query(min_length=3)],
    ):
        return {"q": q}

    @app.get("/query-example/t009/direct")
    async def tutorial009_direct(
        q: str | None = Query(default=None, alias="item-query"),
    ):
        return {"q": q}

    @app.get("/query-example/t009/annotated")
    async def tutorial009_annotated(
        q: Annotated[str | None, Query(alias="item-query")] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t011/direct")
    async def tutorial011_direct(q: list[str] | None = Query(default=None)):  # noqa: B008
        return {"q": q}

    @app.get("/query-example/t011/annotated")
    async def tutorial011_annotated(
        q: Annotated[list[str] | None, Query()] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t012/direct")
    async def tutorial012_direct(
        q: list[str] = Query(default=["oak", "ash"]),  # noqa: B008
    ):
        return {"q": q}

    @app.get("/query-example/t012/annotated")
    async def tutorial012_annotated(
        q: Annotated[list[str], Query()] = ["oak", "ash"],  # noqa: B006
    ):
        return {"q": q}

    @app.get("/query-example/t013/direct")
    async def tutorial013_direct(q: list = Query(default=[])):  # noqa: B008
        return {"q": q}

    @app.get("/query-example/t013/annotated")
    async def tutorial013_annotated(q: Annotated[list, Query()] = []):  # noqa: B006
        return {"q": q}

    @app.get("/query-example/t015/annotated")
    async def tutorial015_annotated(
        id: Annotated[str | None, AfterValidator(_check_id)] = None,
    ):
        return {"id": id}

    return app
