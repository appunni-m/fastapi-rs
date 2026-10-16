#!/usr/bin/env python3
"""Validate the portable source archive required to build FastAPI-RS."""

from __future__ import annotations

import argparse
import hashlib
import re
import tarfile
from pathlib import PurePosixPath
from typing import Any

import tomllib
import yaml
from starlette_rs_source_identity import SOURCE_PATHS


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _source_digest(files: dict[str, bytes], source_prefix: str) -> str:
    selected = []
    for archive_path, content in files.items():
        if not archive_path.startswith(source_prefix):
            continue
        relative = archive_path.removeprefix(source_prefix)
        if any(
            relative == source_path or relative.startswith(source_path.rstrip("/") + "/")
            for source_path in SOURCE_PATHS
        ):
            selected.append((relative, content))
    selected.sort(key=lambda item: item[0])
    _require(selected, "sdist is missing the vendored Starlette-RS build identity files")
    digest = hashlib.sha256()
    for relative, content in selected:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def validate_sdist(path: str) -> dict[str, Any]:
    archive_digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            archive_digest.update(chunk)

    try:
        archive = tarfile.open(path, "r:gz")
    except (OSError, tarfile.TarError) as exc:
        raise ValueError(f"cannot read source archive: {exc}") from exc

    with archive:
        members = archive.getmembers()
        _require(members, "source archive is empty")
        package_roots = {PurePosixPath(member.name).parts[0] for member in members}
        _require(
            len(package_roots) == 1, f"expected one source root, found {sorted(package_roots)}"
        )
        package_root = next(iter(package_roots))
        files: dict[str, bytes] = {}
        seen_paths: set[str] = set()
        for member in members:
            _require(
                bool(member.name) and "\\" not in member.name and "\0" not in member.name,
                f"invalid archive path: {member.name!r}",
            )
            member_path = PurePosixPath(member.name)
            _require(
                member_path.as_posix() == member.name.rstrip("/"),
                f"non-canonical archive path: {member.name}",
            )
            _require(not member_path.is_absolute(), f"absolute archive path: {member.name}")
            _require(".." not in member_path.parts, f"parent traversal in archive: {member.name}")
            normalized_member = member_path.as_posix()
            _require(
                member_path.parts[0] == package_root
                and (
                    len(member_path.parts) > 1
                    or (member.isdir() and normalized_member == package_root)
                ),
                f"archive member is outside its source root: {member.name}",
            )
            _require(
                normalized_member not in seen_paths,
                f"duplicate archive path: {member.name}",
            )
            seen_paths.add(normalized_member)
            _require(
                member.isfile() or member.isdir(),
                f"unsupported archive entry: {member.name}",
            )
            _require(
                not any(part in {"target", ".git", "__pycache__"} for part in member_path.parts)
                and not member.name.endswith((".profraw", ".pyc")),
                f"build or profiling artifact in archive: {member.name}",
            )
            _require(
                not member.name.startswith((f"{package_root}/Users/", f"{package_root}/private/"))
                and "/Users/" not in member.name
                and "/private/tmp/" not in member.name,
                f"machine-local path in archive: {member.name}",
            )
            if member.isfile():
                _require(member.name not in files, f"duplicate archive path: {member.name}")
                content = archive.extractfile(member)
                _require(content is not None, f"cannot read archive member: {member.name}")
                files[member.name] = content.read()

    prefix = f"{package_root}/"
    required = (
        "PKG-INFO",
        "pyproject.toml",
        "Cargo.toml",
        "Cargo.lock",
        "metadata.yaml",
        "README.md",
        "LICENSE.md",
        "THIRD_PARTY_NOTICES.md",
        "fastapi-rs/Cargo.toml",
        "fastapi-rs/build.rs",
        "fastapi-rs/src/lib.rs",
        "fastapi-rs-py/Cargo.toml",
        "fastapi-rs-py/build.rs",
        "fastapi-rs-py/src/lib.rs",
        "fastapi-rs-py/python/fastapi/__init__.py",
        "fastapi-rs-py/python/fastapi_rs/__init__.py",
        "starlette-rs/Cargo.toml",
        "starlette-rs/Cargo.lock",
        "starlette-rs/rust-toolchain.toml",
        "starlette-rs/README.md",
        "starlette-rs/LICENSE.md",
        "starlette-rs/THIRD_PARTY_NOTICES.md",
        "starlette-rs/starlette-rs/Cargo.toml",
        "starlette-rs/starlette-rs/build.rs",
        "starlette-rs/starlette-rs/src/lib.rs",
        "starlette-rs/starlette-rs-py/Cargo.toml",
        "starlette-rs/starlette-rs-py/build.rs",
        "starlette-rs/starlette-rs-py/src/lib.rs",
    )
    missing = [name for name in required if prefix + name not in files]
    _require(not missing, f"source archive omits required build or license files: {missing}")

    pyproject = tomllib.loads(files[prefix + "pyproject.toml"].decode("utf-8"))
    _require(pyproject.get("project", {}).get("name") == "fastapi-rs", "wrong project name")
    maturin = pyproject.get("tool", {}).get("maturin", {})
    _require(
        maturin.get("manifest-path") == "fastapi-rs-py/Cargo.toml"
        and maturin.get("python-source") == "fastapi-rs-py/python",
        "sdist Maturin paths must be relative to the source root",
    )
    _require(
        {"path": "metadata.yaml", "format": "sdist"} in maturin.get("include", []),
        "Maturin sdist configuration must include metadata.yaml",
    )
    workspace = tomllib.loads(files[prefix + "Cargo.toml"].decode("utf-8"))
    _require(
        "starlette-rs" in workspace.get("workspace", {}).get("exclude", []),
        "sdist Cargo workspace must preserve Starlette-RS as its nested workspace",
    )
    dependency = workspace.get("workspace", {}).get("dependencies", {}).get("starlette-rs", {})
    _require(
        dependency.get("path") == "starlette-rs/starlette-rs",
        "sdist Starlette-RS dependency path must be relative and vendored",
    )

    try:
        metadata = yaml.safe_load(files[prefix + "metadata.yaml"].decode("utf-8"))
        expected_source_digest = metadata["starlette_rs"]["source_tree_sha256"]
    except (UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError) as exc:
        raise ValueError(
            f"cannot read Starlette-RS source identity from metadata.yaml: {exc}"
        ) from exc
    _require(
        isinstance(expected_source_digest, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_source_digest) is not None,
        "metadata.yaml has no valid Starlette-RS source_tree_sha256",
    )
    actual_source_digest = _source_digest(files, prefix + "starlette-rs/")
    _require(
        actual_source_digest == expected_source_digest,
        "vendored Starlette-RS source digest mismatch: "
        f"metadata pins {expected_source_digest}, archive has {actual_source_digest}",
    )
    return {
        "status": "valid",
        "archive": path,
        "sha256": archive_digest.hexdigest(),
        "member_count": len(members),
        "starlette_rs_source_tree_sha256": actual_source_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdist", required=True, help="source archive to inspect")
    args = parser.parse_args()
    try:
        result = validate_sdist(args.sdist)
    except (OSError, ValueError, tarfile.TarError) as exc:
        parser.exit(1, f"sdist check failed: {exc}\n")
    import json

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
