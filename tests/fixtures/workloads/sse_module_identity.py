"""Empty argument context for the public FastAPI SSE module identity probe."""


def create_bundles() -> dict[str, dict[str, object]]:
    return {"unused": {"args": [], "kwargs": {}}}
