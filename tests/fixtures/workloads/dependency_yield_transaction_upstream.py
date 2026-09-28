"""Input-only yielded-dependency transaction and exception workload."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import Depends, FastAPI, HTTPException


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Build independent rollback and commit routes around one yielded copy."""

    app = FastAPI()
    database = {"rick": str(factory_input["initial_value"])}

    async def database_transaction():
        working_copy = database.copy()
        try:
            yield working_copy
            database.update(working_copy)
            event_trace.append("committed")
        except HTTPException:
            event_trace.append("caught-http-exception")
            raise
        finally:
            event_trace.append("finalized")

    @app.put("/transaction/rollback")
    async def rollback(
        transaction: dict[str, str] = Depends(database_transaction),  # noqa: B008
    ) -> None:
        transaction["rick"] = "Morty"
        raise HTTPException(status_code=400, detail="rejected")

    @app.put("/transaction/commit")
    async def commit(
        transaction: dict[str, str] = Depends(database_transaction),  # noqa: B008
    ) -> dict[str, str]:
        transaction["rick"] = "Morty"
        return {"message": "committed"}

    @app.get("/transaction/state")
    async def state() -> dict[str, Any]:
        return {"database": dict(database), "events": list(event_trace)}

    return app
