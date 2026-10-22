"""Directly call OAuth2PasswordBearer.__call__ with falsey auto_error."""

from typing import Any

from fastapi import Request
from fastapi.security.oauth2 import OAuth2PasswordBearer


def _arguments(authorization: bytes | None) -> dict[str, Any]:
    headers = []
    if authorization is not None:
        headers.append((b"authorization", authorization))
    request = Request({"type": "http", "headers": headers})
    scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=0)
    return {"args": [scheme, request], "kwargs": {}}


def create_argument_bundles() -> dict[str, dict[str, Any]]:
    return {
        "missing-authorization": _arguments(None),
        "non-bearer-authorization": _arguments(b"Basic preview-token"),
        "bearer-authorization": _arguments(b"Bearer preview-token"),
    }
