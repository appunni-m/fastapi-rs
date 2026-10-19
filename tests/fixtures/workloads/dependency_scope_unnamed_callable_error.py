"""Input-only route construction for the unnamed dependency error branch."""

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI


def _function_scoped_dependency() -> Any:
    yield object()


class _RequestScopedCallable:
    def __call__(
        self,
        child: Annotated[Any, Depends(_function_scoped_dependency, scope="function")],
    ) -> Any:
        yield child


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Declare an invalid scope graph through an unnamed callable instance."""
    del factory_input, event_trace
    app = FastAPI()
    request_scoped_callable = _RequestScopedCallable()

    @app.get("/invalid-unnamed-scope")
    def read_value(
        value: Annotated[Any, Depends(request_scoped_callable)],
    ) -> None:
        del value

    return app
