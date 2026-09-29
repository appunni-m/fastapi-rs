"""Input values for the narrow Pydantic Core encoder compatibility bridge.

Pinned FastAPI source evidence (0.141.1,
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f):

* ``fastapi/encoders.py`` SHA-256
  ``4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad``:
  imports ``PydanticUndefinedType`` at line 27, registers ``Url`` and
  ``AnyUrl`` as string encoders at lines 103 and 110–111, and maps undefined
  instances to ``None`` at lines 279–280.
* ``fastapi/_compat/v2.py`` SHA-256
  ``b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9``:
  imports ``Url`` and ``PydanticUndefined`` from Pydantic Core at lines 32–34.

The recipe contains only values passed to the public encoder; it stores no
expected outputs.
"""

from __future__ import annotations

from pydantic import AnyUrl
from pydantic_core import PydanticUndefined, Url


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build the three independent values for FastAPI's public encoder."""
    return {
        "undefined.value": {"args": [{"value": PydanticUndefined}], "kwargs": {}},
        "url.raw-core": {
            "args": [{"value": Url("https://example.com/path?kind=core")}],
            "kwargs": {},
        },
        "url.public-any": {
            "args": [{"value": AnyUrl("https://example.com/path?kind=pydantic")}],
            "kwargs": {},
        },
    }
