"""Input-only constructor arguments for public WebSocketException observations."""


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "explicit-code-reason": {
            "args": [],
            "kwargs": {"code": 1008, "reason": "policy"},
        },
        "omitted-reason": {
            "args": [],
            "kwargs": {"code": 1003},
        },
    }
