"""Inputs for direct optional FastAPI JSON response constructor parity."""


def create_bundles() -> dict[str, dict[str, object]]:
    content = {"message": "optional serializer"}
    return {
        "orjson-content": {"args": [content], "kwargs": {}},
        "ujson-content": {"args": [content], "kwargs": {}},
    }
