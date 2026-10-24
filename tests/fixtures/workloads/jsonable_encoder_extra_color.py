"""Independent input for FastAPI's optional Pydantic Extra Types Color path."""

from pydantic_extra_types.color import Color


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Return a nested Color value for the public jsonable_encoder call."""
    return {
        "extra-color.nested": {
            "args": [{"shade": Color("blue")}],
            "kwargs": {},
        }
    }
