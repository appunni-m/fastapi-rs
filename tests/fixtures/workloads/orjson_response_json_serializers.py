"""Independent arguments for direct ORJSONResponse.render parity."""


def create_bundles() -> dict[str, dict[str, object]]:
    return {
        "render-content": {
            "args": [None, {"message": "unicode: café/λ", 7: "integer-key"}],
            "kwargs": {},
        },
        "render-unsupported-object": {
            "args": [None, {"bad": object()}],
            "kwargs": {},
        },
    }
