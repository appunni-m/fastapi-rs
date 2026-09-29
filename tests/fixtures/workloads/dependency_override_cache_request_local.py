"""Independent input-only workload for override dependency cache reuse."""

from fastapi import Depends, FastAPI


def create_app(
    factory_input: dict[str, object] | None = None,
    event_trace: list[dict[str, object]] | None = None,
) -> FastAPI:
    app = FastAPI()
    replacement_calls = {"count": 0}

    def original_dependency() -> int:
        return -1

    def replacement_dependency() -> int:
        replacement_calls["count"] += 1
        return replacement_calls["count"]

    @app.get("/override-cache")
    def read_override_cache(
        first: int = Depends(original_dependency),
        second: int = Depends(original_dependency),
    ) -> dict[str, int]:
        return {
            "first": first,
            "second": second,
            "replacement_calls": replacement_calls["count"],
        }

    app.dependency_overrides[original_dependency] = replacement_dependency
    return app
