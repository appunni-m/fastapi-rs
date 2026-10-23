"""Independent direct API inputs for FastAPI UploadFile I/O parity."""

from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile


def _file(content: bytes, *, position: int = 0) -> UploadFile:
    file = BytesIO(content)
    file.seek(position)
    return UploadFile(file=file, filename="payload.bin", size=len(content))


def _bundle(*args: object) -> dict[str, object]:
    return {"args": list(args), "kwargs": {}}


def create_bundles() -> dict[str, dict[str, object]]:
    seek_file = _file(b"012345")
    write_file = _file(b"abcdef", position=2)
    eof_file = _file(b"end")
    eof_offset = len(b"end")
    close_file = _file(b"closed")
    negative_seek_file = _file(b"negative")
    write_closed_file = _file(b"closed-write")

    return {
        "read-full": _bundle(_file(b"\x00A\xffB")),
        "read-limited": _bundle(_file(b"\x00A\xffB"), 2),
        "seek-then-read-seek": _bundle(seek_file, 3),
        "seek-then-read-read": _bundle(seek_file),
        "write-then-read-write": _bundle(write_file, b"XY"),
        "write-then-read-seek": _bundle(write_file, 0),
        "write-then-read-read": _bundle(write_file),
        "read-at-eof-seek": _bundle(eof_file, eof_offset),
        "read-at-eof-read": _bundle(eof_file),
        "close-then-read-close": _bundle(close_file),
        "close-then-read-read": _bundle(close_file),
        "negative-seek": _bundle(negative_seek_file, -1),
        "write-after-close-close": _bundle(write_closed_file),
        "write-after-close-write": _bundle(write_closed_file, b"X"),
    }
