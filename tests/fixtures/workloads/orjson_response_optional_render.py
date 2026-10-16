"""Input arguments for the optional ORJSONResponse render contract."""


def create_bundles() -> dict[str, dict[str, object]]:
    return {
        "render-content": {
            "args": [None, {"message": "optional serializer"}],
            "kwargs": {},
        }
    }
