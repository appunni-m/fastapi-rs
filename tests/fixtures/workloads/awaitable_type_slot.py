"""One public request for type-level await-slot lookup in FastAPI paths."""

import inspect
from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI


class ShadowedAwaitable:
    def __init__(self, role: str, value: Any) -> None:
        self.role = role
        self.value = value
        self.__await__ = None

    def __await__(self) -> Any:
        async def resolve() -> dict[str, Any]:
            return {"role": self.role, "value": self.value}

        return resolve().__await__()


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> Any:
    app = FastAPI()

    @inspect.markcoroutinefunction
    def dependency() -> Any:
        return ShadowedAwaitable("dependency", 19)

    @inspect.markcoroutinefunction
    def endpoint(value: Annotated[Any, Depends(dependency)]) -> Any:
        return ShadowedAwaitable("endpoint", value)

    app.get("/probe", response_model=None)(endpoint)
    return app
