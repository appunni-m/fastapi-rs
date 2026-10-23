"""Independent arguments for direct UJSONResponse.render parity."""


class UnsupportedValue:
    def __repr__(self) -> str:
        return "UnsupportedValue()"


def create_bundles() -> dict[str, dict[str, object]]:
    return {
        "render-content": {
            "args": [None, {"message": "unicode: café/λ"}],
            "kwargs": {},
        },
        "render-unsupported-object": {
            "args": [None, {"bad": UnsupportedValue()}],
            "kwargs": {},
        },
    }
