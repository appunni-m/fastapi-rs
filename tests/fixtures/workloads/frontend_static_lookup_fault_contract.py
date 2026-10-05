"""Target-only public outcomes for FastAPI frontend lookup fault contracts."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one isolated frontend app and retain its directory through dispatch."""
    del factory_input, event_trace
    app = FastAPI()
    directory = TemporaryDirectory(prefix="fastapi-frontend-lookup-fault-")
    (Path(directory.name) / "index.html").write_text("frontend", encoding="utf-8")
    app.state.frontend_lookup_fault_directories = [directory]
    app.frontend("/", directory=directory.name)
    return app
