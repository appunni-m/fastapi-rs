"""Build the native target against the selected Starlette-RS source checkout."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def _install_editable_target(uv: str, target_python: Path) -> int:
    lockfile = ROOT / "Cargo.lock"
    lock_before = lockfile.read_bytes()
    lock_mode = lockfile.stat().st_mode & 0o7777
    environment = os.environ.copy()
    environment["PYO3_PYTHON"] = str(target_python)
    try:
        completed = subprocess.run(
            [
                uv,
                "pip",
                "install",
                "--python",
                str(target_python),
                "--no-deps",
                "--editable",
                str(ROOT),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
        )
    finally:
        try:
            lock_after = lockfile.read_bytes()
        except FileNotFoundError:
            lock_after = None
        if lock_after != lock_before:
            _atomic_write(lockfile, lock_before, lock_mode)
            print("restored Cargo.lock after editable package metadata build")
    return completed.returncode


def _atomic_write(destination: Path, content: bytes, mode: int) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _workspace_overlay(starlette_rs_source: Path, overlay_root: Path) -> None:
    manifest = ROOT / "Cargo.toml"
    try:
        manifest_text = manifest.read_text(encoding="utf-8")
        manifest_data = tomllib.loads(manifest_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"cannot read Cargo workspace manifest: {exc}") from exc

    dependency = manifest_data.get("workspace", {}).get("dependencies", {}).get("starlette-rs")
    if not isinstance(dependency, dict) or not isinstance(dependency.get("path"), str):
        raise SystemExit("Cargo.toml must declare starlette-rs as a workspace path dependency")
    old_path = f"path = {json.dumps(dependency['path'])}"
    if manifest_text.count(old_path) != 1:
        raise SystemExit("Cargo.toml starlette-rs workspace dependency path is ambiguous")
    pinned_path = starlette_rs_source.resolve() / "starlette-rs"
    overlay_text = manifest_text.replace(old_path, f"path = {json.dumps(str(pinned_path))}", 1)

    overlay_root.mkdir(parents=True, exist_ok=True)
    (overlay_root / "Cargo.toml").write_text(overlay_text, encoding="utf-8")
    shutil.copy2(ROOT / "Cargo.lock", overlay_root / "Cargo.lock")
    for filename in ("README.md", "LICENSE.md", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / filename, overlay_root / filename)

    members = manifest_data.get("workspace", {}).get("members", [])
    if not members:
        raise SystemExit("Cargo.toml does not declare workspace members")
    for member in members:
        member_path = Path(member)
        if member_path.is_absolute() or ".." in member_path.parts:
            raise SystemExit(f"unsupported non-workspace Cargo member path: {member}")
        source_member = ROOT / member_path
        if not source_member.exists():
            raise SystemExit(f"Cargo workspace member does not exist: {member}")
        link_path = overlay_root / member_path
        link_path.parent.mkdir(parents=True, exist_ok=True)
        link_path.symlink_to(source_member, target_is_directory=source_member.is_dir())


def _verify_overlay_metadata(
    overlay_root: Path,
    starlette_rs_source: Path,
    cargo_command: list[str],
    *,
    all_features: bool = False,
) -> None:
    command = [
        *cargo_command,
        "metadata",
        "--manifest-path",
        str(overlay_root / "Cargo.toml"),
        "--locked",
        "--offline",
        "--format-version",
        "1",
    ]
    if all_features:
        command.append("--all-features")
    else:
        command.extend(["--features", "pyo3/extension-module"])
    completed = subprocess.run(
        command,
        cwd=overlay_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode:
        raise SystemExit(
            "cannot verify target Cargo workspace before build: "
            + (completed.stderr.strip() or "cargo metadata failed")
        )
    try:
        metadata = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Cargo returned malformed dependency metadata: {exc}") from exc

    if Path(metadata.get("workspace_root", "")).resolve() != overlay_root.resolve():
        raise SystemExit("Cargo metadata did not resolve this FastAPI overlay as its workspace")
    packages = {package["id"]: package for package in metadata.get("packages", [])}
    workspace_members = set(metadata.get("workspace_members", []))
    expected_members = {
        "fastapi-rs": ROOT / "fastapi-rs/Cargo.toml",
        "fastapi-rs-py": ROOT / "fastapi-rs-py/Cargo.toml",
    }
    member_packages: dict[str, dict[str, object]] = {}
    for name, source_manifest in expected_members.items():
        matches = [
            package
            for package in packages.values()
            if package.get("name") == name
            and Path(package.get("manifest_path", "")).resolve() == source_manifest.resolve()
            and package.get("id") in workspace_members
        ]
        if len(matches) != 1:
            raise SystemExit(
                "Cargo metadata does not prove the overlay contains FastAPI workspace member "
                f"{name}"
            )
        member_packages[name] = matches[0]

    root_node = next(
        (
            node
            for node in metadata.get("resolve", {}).get("nodes", [])
            if node.get("id") == member_packages["fastapi-rs"].get("id")
        ),
        None,
    )
    if root_node is None:
        raise SystemExit("Cargo metadata omitted the FastAPI-RS implementation dependency node")
    starlette_dependencies = [
        packages[dependency["pkg"]]
        for dependency in root_node.get("deps", [])
        if packages.get(dependency.get("pkg"), {}).get("name") == "starlette-rs"
    ]
    expected_starlette_manifest = (starlette_rs_source / "starlette-rs/Cargo.toml").resolve()
    if (
        len(starlette_dependencies) != 1
        or Path(starlette_dependencies[0].get("manifest_path", "")).resolve()
        != expected_starlette_manifest
    ):
        actual = [package.get("manifest_path") for package in starlette_dependencies]
        raise SystemExit(
            "FastAPI-RS Cargo metadata resolved Starlette-RS outside the selected checkout: "
            f"expected {expected_starlette_manifest}, got {actual}"
        )


def _extension_suffix(target_python: Path) -> str:
    result = subprocess.run(
        [
            str(target_python),
            "-c",
            "import importlib.machinery; print(next("
            "suffix for suffix in importlib.machinery.EXTENSION_SUFFIXES "
            "if suffix.startswith('.abi3')))",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "cannot identify target Python extension suffix")
    suffix = result.stdout.strip()
    if not suffix:
        raise SystemExit("target Python has no abi3 extension suffix")
    return suffix


def _install_extension_atomically(source: Path, destination: Path) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        shutil.copy2(source, temporary_path)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, help="target virtualenv Python")
    parser.add_argument("--uv", default="uv", help="uv executable")
    parser.add_argument("--cargo", default="cargo", help="Cargo command (supports wrappers)")
    parser.add_argument(
        "--clippy", action="store_true", help="run strict workspace Clippy without installing"
    )
    parser.add_argument(
        "--starlette-rs-source", required=True, type=Path, help="selected Starlette-RS checkout"
    )
    args = parser.parse_args()
    starlette_rs_source = args.starlette_rs_source.resolve()
    if not starlette_rs_source.is_dir():
        raise SystemExit(f"Starlette-RS source directory does not exist: {starlette_rs_source}")
    cargo_command = shlex.split(args.cargo)
    if not cargo_command:
        raise SystemExit("Cargo command must not be empty")
    overlay_parent = ROOT
    default_target_directory = ROOT / "target"
    default_target_directory.mkdir(exist_ok=True)
    target_directory = Path(os.environ.get("CARGO_TARGET_DIR", default_target_directory)).resolve()
    with tempfile.TemporaryDirectory(
        prefix=".fastapi-rs-build-", dir=overlay_parent
    ) as temporary_directory:
        overlay_root = Path(temporary_directory)
        _workspace_overlay(starlette_rs_source, overlay_root)
        _verify_overlay_metadata(
            overlay_root,
            starlette_rs_source,
            cargo_command,
            all_features=args.clippy,
        )
        environment = os.environ.copy()
        environment["CARGO_TARGET_DIR"] = str(target_directory)
        if args.clippy:
            command = [
                *cargo_command,
                "clippy",
                "--manifest-path",
                str(overlay_root / "Cargo.toml"),
                "--locked",
                "--offline",
                "--workspace",
                "--all-targets",
                "--all-features",
                "--",
                "-D",
                "warnings",
            ]
            return subprocess.run(
                command, cwd=overlay_root, env=environment, check=False
            ).returncode

        if args.python is None:
            raise SystemExit("--python is required unless --clippy is selected")
        target_python = args.python.absolute()
        if not target_python.is_file():
            raise SystemExit(f"target Python does not exist: {target_python}")
        editable_status = _install_editable_target(args.uv, target_python)
        if editable_status:
            return editable_status
        environment["PYO3_PYTHON"] = str(target_python)
        command = [
            *cargo_command,
            "build",
            "--manifest-path",
            str(overlay_root / "Cargo.toml"),
            "--locked",
            "--offline",
            "--release",
            "--features",
            "pyo3/extension-module",
        ]
        completed = subprocess.run(command, cwd=overlay_root, env=environment, check=False)
        if completed.returncode:
            return completed.returncode

        artifact_candidates = [
            target_directory / "release" / name
            for name in ("lib_core.dylib", "lib_core.so", "_core.dll", "core.dll")
        ]
        artifacts = [path for path in artifact_candidates if path.is_file()]
        if len(artifacts) != 1:
            raise SystemExit(
                f"expected one built FastAPI-RS library artifact, found {len(artifacts)}"
            )
        suffix = _extension_suffix(target_python)
        destination = ROOT / "fastapi-rs-py/python/fastapi_rs" / f"_core{suffix}"
        _install_extension_atomically(artifacts[0], destination)
    print(f"installed native extension built against {starlette_rs_source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
