"""Independent FileResponse input for the additional-response tutorials."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

_PNG_LIKE_BYTES = b"independent file-response input bytes"
_FIXED_MTIME = 1_700_000_000


def create_app() -> FastAPI:
    app = FastAPI()
    asset_directory = tempfile.TemporaryDirectory()
    image_path = Path(asset_directory.name) / "image.png"
    image_path.write_bytes(_PNG_LIKE_BYTES)
    os.utime(image_path, (_FIXED_MTIME, _FIXED_MTIME))
    app.state.asset_directory = asset_directory

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, img: bool = False):
        if img:
            return FileResponse(image_path)
        return {"id": item_id, "value": "independent item"}

    return app
