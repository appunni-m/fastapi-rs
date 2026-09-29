"""Independent sync dependencies for nested request-cache semantics."""

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Dependency Cache Source Wave", version="1.0.0")
    state = {"counter": 0}

    def next_counter() -> int:
        state["counter"] += 1
        return state["counter"]

    def parent_value(value: int = Depends(next_counter)) -> int:
        return value

    @app.get("/cache/shared-child")
    async def shared_child(
        subcounter: int = Depends(parent_value),
        counter: int = Depends(next_counter),
    ):
        return {"counter": counter, "subcounter": subcounter}

    @app.get("/cache/shared-child-bypass")
    async def shared_child_bypass(
        subcounter: int = Depends(parent_value),
        counter: int = Depends(next_counter, use_cache=False),
    ):
        return {"counter": counter, "subcounter": subcounter}

    return app
