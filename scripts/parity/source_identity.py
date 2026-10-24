"""Stable identities for the source trees used by parity workers."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


class SourceIdentityError(RuntimeError):
    """A source tree could not be enumerated for its identity digest."""


FASTAPI_RS_RUNTIME_SCOPE_ID = "fastapi-rs-runtime-v1"
FASTAPI_RS_RUNTIME_FILES = (
    "Cargo.toml",
    "Cargo.lock",
    "rust-toolchain.toml",
    "pyproject.toml",
    "fastapi-rs/Cargo.toml",
    "fastapi-rs/build.rs",
    "fastapi-rs-py/Cargo.toml",
    "fastapi-rs-py/build.rs",
    "requirements/target-runtime-cpython-3.12.13.lock",
)
FASTAPI_RS_RUNTIME_PREFIXES = (
    "fastapi-rs/src/",
    "fastapi-rs-py/src/",
    "fastapi-rs-py/python/",
)
STARLETTE_RS_RUNTIME_SCOPE_ID = "starlette-rs-runtime-v1"
STARLETTE_RS_RUNTIME_FILES = (
    "Cargo.toml",
    "Cargo.lock",
    "rust-toolchain.toml",
    "pyproject.toml",
    "starlette-rs/Cargo.toml",
    "starlette-rs/build.rs",
    "starlette-rs-py/Cargo.toml",
    "starlette-rs-py/build.rs",
)
STARLETTE_RS_RUNTIME_PREFIXES = (
    "starlette-rs/src/",
    "starlette-rs-py/src/",
    "starlette-rs-py/python/",
)
INDEXED_PARITY_HARNESS_SCOPE_ID = "indexed-parity-harness-v1"
INDEXED_PARITY_HARNESS_FILES = ("scripts/build_parity_inputs.py",)
INDEXED_PARITY_HARNESS_PREFIXES = ("scripts/parity/",)


def _listed_source_files(root: Path, label: str) -> list[bytes]:
    """List tracked and non-ignored source paths, including working-tree edits."""
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
    return sorted(set(entry for entry in completed.stdout.split(b"\0") if entry))


def _hash_source_files(root: Path, label: str, paths: list[bytes]) -> str:
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


def source_tree_sha256(root: Path, label: str) -> str:
    """Hash every tracked and non-ignored source file, including working-tree edits."""
    paths = _listed_source_files(root, label)
    return _hash_source_files(root, label, paths)


def source_scope_sha256(
    root: Path,
    label: str,
    scope_id: str,
    *,
    files: tuple[str, ...],
    prefixes: tuple[str, ...],
) -> str:
    """Hash only reviewed runtime paths and fail if any required path is absent."""
    if not scope_id or not files or not prefixes:
        raise SourceIdentityError(f"{label} source scope is incomplete")
    for relative in files:
        if not (root / relative).is_file():
            raise SourceIdentityError(f"{label} source scope file is missing: {relative}")
    for prefix in prefixes:
        if not (root / prefix).is_dir():
            raise SourceIdentityError(f"{label} source scope directory is missing: {prefix}")

    listed = _listed_source_files(root, label)
    file_bytes = {os.fsencode(relative) for relative in files}
    prefix_bytes = tuple(os.fsencode(prefix) for prefix in prefixes)
    scoped = [
        relative
        for relative in listed
        if relative in file_bytes or any(relative.startswith(prefix) for prefix in prefix_bytes)
    ]
    scoped_set = set(scoped)
    missing_files = file_bytes - scoped_set
    if missing_files:
        missing = ", ".join(os.fsdecode(path) for path in sorted(missing_files))
        raise SourceIdentityError(f"{label} source scope files are not indexed: {missing}")
    for prefix in prefix_bytes:
        if not any(relative.startswith(prefix) for relative in scoped):
            raise SourceIdentityError(
                f"{label} source scope contains no files under {os.fsdecode(prefix)}"
            )

    digest = hashlib.sha256()
    digest.update(scope_id.encode("utf-8"))
    digest.update(b"\0")
    digest.update(_hash_source_files(root, label, scoped).encode("ascii"))
    return digest.hexdigest()


def fastapi_rs_runtime_source_scope_sha256(target_source: Path, starlette_rs_source: Path) -> str:
    """Hash the native and Python runtime sources used by indexed parity workers."""
    return combine_digests(
        {
            FASTAPI_RS_RUNTIME_SCOPE_ID: source_scope_sha256(
                target_source,
                "FastAPI-RS",
                FASTAPI_RS_RUNTIME_SCOPE_ID,
                files=FASTAPI_RS_RUNTIME_FILES,
                prefixes=FASTAPI_RS_RUNTIME_PREFIXES,
            ),
            STARLETTE_RS_RUNTIME_SCOPE_ID: source_scope_sha256(
                starlette_rs_source,
                "Starlette-RS",
                STARLETTE_RS_RUNTIME_SCOPE_ID,
                files=STARLETTE_RS_RUNTIME_FILES,
                prefixes=STARLETTE_RS_RUNTIME_PREFIXES,
            ),
        }
    )


def indexed_parity_harness_source_scope_sha256(root: Path) -> str:
    """Hash the indexed runner, workers, comparator, contracts, and recipe loader."""
    return source_scope_sha256(
        root,
        "indexed parity harness",
        INDEXED_PARITY_HARNESS_SCOPE_ID,
        files=INDEXED_PARITY_HARNESS_FILES,
        prefixes=INDEXED_PARITY_HARNESS_PREFIXES,
    )


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
