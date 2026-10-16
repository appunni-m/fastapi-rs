"""Stable identities for the source trees used by parity workers."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


class SourceIdentityError(RuntimeError):
    """A source tree could not be enumerated for its identity digest."""


def source_tree_sha256(root: Path, label: str) -> str:
    """Hash tracked and non-ignored source files, including working-tree edits."""
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        check=False,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SourceIdentityError(f"cannot enumerate {label} source files: {detail}")

    paths = sorted(set(entry for entry in completed.stdout.split(b"\0") if entry))
    digest = hashlib.sha256()
    for relative_bytes in paths:
        relative = os.fsdecode(relative_bytes)
        path = root / relative
        digest.update(relative_bytes)
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"symlink\0")
            digest.update(os.fsencode(os.readlink(path)))
        elif path.is_file():
            digest.update(b"file\0")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            # A deleted tracked file must affect the identity too.
            digest.update(b"missing\0")
        digest.update(b"\0")
    return digest.hexdigest()


def combine_digests(entries: dict[str, str]) -> str:
    """Combine named component digests in a stable, unambiguous order."""
    digest = hashlib.sha256()
    for name, value in sorted(entries.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(value.encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def fastapi_rs_source_tree_sha256(target_source: Path, starlette_rs_source: Path) -> str:
    """Return the parity target digest for FastAPI-RS plus its Starlette-RS source."""
    return combine_digests(
        {
            "fastapi-rs": source_tree_sha256(target_source, "FastAPI-RS"),
            "starlette-rs": source_tree_sha256(starlette_rs_source, "Starlette-RS"),
        }
    )
