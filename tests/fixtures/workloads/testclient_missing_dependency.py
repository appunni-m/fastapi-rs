"""Construct a FastAPI app for the core-profile TestClient dependency probe."""

from fastapi import FastAPI


def create_bundles() -> dict[str, dict[str, object]]:
    app = FastAPI()
    return {"client": {"args": [app], "kwargs": {}}}
