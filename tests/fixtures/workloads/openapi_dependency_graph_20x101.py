"""Input builder for the cold OpenAPI dependency graph workload."""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends, FastAPI

LAST_DEPENDENCY_INDEX = 100
ROUTE_COUNT = 20
ROUTE_PATH_PREFIX = "/openapi-route-"


def _make_dependency(index: int, next_dependency: Callable[..., Any] | None) -> Callable[..., Any]:
    if next_dependency is None:

        def dependency(query_value: int = index) -> str:
            return str(query_value)

    else:

        async def dependency(
            sub_dependency: Annotated[str, Depends(next_dependency)],
            query_value: int = index,
        ) -> str:
            return f"{query_value} -> {sub_dependency}"

    dependency.__name__ = f"dependency_{index}"
    return dependency


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build the benchmark's route/dependency shape as input, without expectations."""
    dependencies: dict[int, Callable[..., Any]] = {}
    for index in reversed(range(LAST_DEPENDENCY_INDEX + 1)):
        dependencies[index] = _make_dependency(
            index,
            dependencies.get(index + 1),
        )

    async def endpoint(value: Annotated[str, Depends(dependencies[0])]) -> dict[str, str]:
        return {"value": value}

    app = FastAPI()
    for route_index in range(ROUTE_COUNT):
        app.add_api_route(
            f"{ROUTE_PATH_PREFIX}{route_index}",
            endpoint,
            methods=["GET"],
        )

    return {"openapi-dependency-graph": {"args": [app], "kwargs": {}}}
