"""Independent app and dependency graph for uncovered tutorial samples."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


class CatalogWindow:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 3) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


class SearchPhrase:
    def __init__(self, required_text: str) -> None:
        self.required_text = required_text

    def __call__(self, phrase: str = "") -> bool:
        return bool(phrase and self.required_text in phrase)


class OwnershipFailure(Exception):
    pass


def create_app() -> FastAPI:
    app = FastAPI()

    archive = [
        {"title": "Amber Field Guide"},
        {"title": "Cedar Atlas"},
        {"title": "Willow Almanac"},
    ]

    async def common_listing(q: str | None = None, skip: int = 0, limit: int = 3):
        return {"q": q, "skip": skip, "limit": limit}

    @app.get("/library/")
    # Keep this legacy signature form in the workload under review.
    async def read_library(parameters: dict = Depends(common_listing)):  # noqa: B008
        return parameters

    @app.get("/members/")
    async def read_members(
        parameters: Annotated[dict[str, str | int | None], Depends(common_listing)],
    ):
        return parameters

    def catalog_payload(parameters: CatalogWindow) -> dict[str, object]:
        result: dict[str, object] = {
            "items": archive[parameters.skip : parameters.skip + parameters.limit]
        }
        if parameters.q:
            result["q"] = parameters.q
        return result

    @app.get("/catalog/class/")
    async def read_catalog_class(
        parameters: Annotated[CatalogWindow, Depends(CatalogWindow)],
    ):
        return catalog_payload(parameters)

    @app.get("/catalog/untyped/")
    # This route deliberately preserves an untyped Depends default.
    async def read_catalog_untyped(parameters=Depends(CatalogWindow)):  # noqa: B008
        return catalog_payload(parameters)

    @app.get("/catalog/inferred/")
    async def read_catalog_inferred(parameters: Annotated[CatalogWindow, Depends()]):
        return catalog_payload(parameters)

    async def check_access_token(
        x_access_token: Annotated[str, Header()],
    ) -> None:
        if x_access_token != "token-for-review":
            raise HTTPException(status_code=400, detail="access token rejected")

    async def check_archive_key(
        x_archive_key: Annotated[str, Header()],
    ) -> str:
        if x_archive_key != "key-for-review":
            raise HTTPException(status_code=400, detail="archive key rejected")
        return x_archive_key

    @app.get(
        "/vault/",
        dependencies=[Depends(check_access_token), Depends(check_archive_key)],
    )
    async def read_vault() -> list[dict[str, str]]:
        return [{"label": "North Shelf"}, {"label": "South Shelf"}]

    @app.get("/search/")
    async def search_catalog(
        matched: Annotated[bool, Depends(SearchPhrase("willow"))],
    ) -> dict[str, bool]:
        return {"matched": matched}

    async def current_account():
        try:
            yield "account-north"
        except OwnershipFailure as error:
            raise HTTPException(status_code=400, detail=f"access denied: {error}") from error

    records = {
        "compass": {"description": "Trail compass", "owner": "account-south"},
        "field-book": {"description": "Weather notes", "owner": "account-north"},
    }

    @app.get("/assets/{asset_id}")
    async def read_asset(
        asset_id: str,
        account: Annotated[str, Depends(current_account)],
    ) -> dict[str, str]:
        if asset_id not in records:
            raise HTTPException(status_code=404, detail="asset not found")
        asset = records[asset_id]
        if asset["owner"] != account:
            raise OwnershipFailure(account)
        return asset

    return app
