"""Empty argument bundles for direct FastAPI SSE API metadata probes."""


def create_bundles() -> dict[str, dict[str, object]]:
    return {"unused": {"args": [], "kwargs": {}}}
