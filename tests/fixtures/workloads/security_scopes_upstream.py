"""Independently authored SecurityScopes and dependency-caching workload."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Security
from fastapi.security import SecurityScopes


def create_app() -> FastAPI:
    app = FastAPI()
    calls = {"database": 0}

    def get_database() -> str:
        calls["database"] += 1
        return f"db_{calls['database']}"

    def get_user(database: Annotated[str, Depends(get_database)]) -> str:
        return f"user_from_{database}"

    @app.get("/scopes/cache-once")
    def dependency_cache_once(
        database: Annotated[str, Depends(get_database)],
        user: Annotated[str, Security(get_user, scopes=["read"])],
    ) -> dict[str, str]:
        return {"database": database, "user": user}

    async def collect_first(scopes: SecurityScopes) -> list[str]:
        return scopes.scopes

    async def collect_second(scopes: SecurityScopes) -> list[str]:
        return scopes.scopes

    async def collect_both(
        first: Annotated[list[str], Security(collect_first, scopes=["scope1"])],
        second: Annotated[list[str], Security(collect_second, scopes=["scope2"])],
    ) -> dict[str, list[str]]:
        return {"first": first, "second": second}

    @app.get("/scopes/non-propagating")
    async def read_non_propagating_scopes(
        scopes: Annotated[dict[str, list[str]], Security(collect_both, scopes=["scope3"])],
    ) -> dict[str, list[str]]:
        return scopes

    call_counts = {
        "get_db_session": 0,
        "get_current_user": 0,
        "get_user_me": 0,
        "get_user_items": 0,
    }

    def get_db_session() -> str:
        call_counts["get_db_session"] += 1
        return f"db_session_{call_counts['get_db_session']}"

    def get_current_user(
        security_scopes: SecurityScopes,
        db_session: Annotated[str, Depends(get_db_session)],
    ) -> dict[str, Any]:
        call_counts["get_current_user"] += 1
        return {
            "user": f"user_{call_counts['get_current_user']}",
            "scopes": security_scopes.scopes,
            "db_session": db_session,
        }

    def get_user_me(
        current_user: Annotated[dict[str, Any], Security(get_current_user, scopes=["me"])],
    ) -> dict[str, Any]:
        call_counts["get_user_me"] += 1
        return {
            "user_me": f"user_me_{call_counts['get_user_me']}",
            "current_user": current_user,
        }

    def get_user_items(
        user_me: Annotated[dict[str, Any], Depends(get_user_me)],
    ) -> dict[str, Any]:
        call_counts["get_user_items"] += 1
        return {
            "user_items": f"user_items_{call_counts['get_user_items']}",
            "user_me": user_me,
        }

    @app.get("/scopes/sub-dependency-cache")
    def read_sub_dependency_cache(
        user_me: Annotated[dict[str, Any], Depends(get_user_me)],
        user_items: Annotated[dict[str, Any], Security(get_user_items, scopes=["items"])],
    ) -> dict[str, Any]:
        return {"user_me": user_me, "user_items": user_items}

    return app
