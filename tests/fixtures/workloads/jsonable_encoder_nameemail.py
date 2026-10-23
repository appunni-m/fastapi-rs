"""Independent direct-call input for the Pydantic NameEmail encoder path."""

from pydantic import TypeAdapter
from pydantic.networks import NameEmail


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build one validated NameEmail value for jsonable_encoder."""
    value = TypeAdapter(NameEmail).validate_python("Ada Lovelace <ada@example.org>")
    return {"name-email.validated": {"args": [value], "kwargs": {}}}
