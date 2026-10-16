"""Hash the Starlette-RS source inputs consumed by FastAPI-RS build checks."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

SOURCE_PATHS = (
    "Cargo.toml",
    "Cargo.lock",
    "rust-toolchain.toml",
    "starlette-rs/Cargo.toml",
    "starlette-rs/build.rs",
    "starlette-rs/src",
    "starlette-rs-py/Cargo.toml",
    "starlette-rs-py/build.rs",
    "starlette-rs-py/src",
    "starlette-rs-py/python",
)


def source_tree_files(root: Path, *, tracked_only: bool) -> list[Path]:
    """Return the pinned build-identity files, relative to a checkout or sdist copy."""
    root = root.resolve()
    if tracked_only:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", *SOURCE_PATHS],
            check=False,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(
                result.stderr.decode("utf-8", errors="replace").strip()
                or f"cannot list tracked Starlette-RS sources in {root}"
            )
        paths = [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]
    else:
        paths = []
        for source in SOURCE_PATHS:
            candidate = root / source
            if candidate.is_file():
                paths.append(Path(source))
            elif candidate.is_dir():
                paths.extend(
                    path.relative_to(root) for path in candidate.rglob("*") if path.is_file()
                )
            else:
                raise RuntimeError(f"vendored Starlette-RS build input is missing: {source}")
        paths = [
            path
            for path in paths
            if not any(part in {".git", "target", "__pycache__"} for part in path.parts)
            and path.suffix not in {".profraw", ".pyc"}
        ]

    unique = sorted(set(paths), key=lambda path: path.as_posix())
    if not unique:
        raise RuntimeError(f"no Starlette-RS build identity files found under {root}")
    for path in unique:
        if path.is_absolute() or ".." in path.parts or (root / path).is_symlink():
            raise RuntimeError(f"invalid Starlette-RS build identity path: {path}")
        if not (root / path).is_file():
            raise RuntimeError(f"Starlette-RS build identity file is missing: {path}")
    return unique


def source_tree_sha256(root: Path, *, tracked_only: bool) -> str:
    """Hash sorted relative paths and bytes with NUL separators for reproducibility."""
    root = root.resolve()
    digest = hashlib.sha256()
    for path in source_tree_files(root, tracked_only=tracked_only):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / path).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
