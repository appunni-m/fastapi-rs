"""Private Python binding namespace used by the FastAPI-RS package."""

from ._core import identity, require_supported_scope, scope_kind

__all__ = ["identity", "require_supported_scope", "scope_kind"]
